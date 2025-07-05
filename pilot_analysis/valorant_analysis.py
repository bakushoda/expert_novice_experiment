import pandas as pd
import numpy as np
import os
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway, kruskal, levene, shapiro
try:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("注意: statsmodelsがインストールされていません。多重比較検定をスキップします。")
    print("多重比較を実行するには以下を実行してください: pip install statsmodels")
import warnings
warnings.filterwarnings('ignore')

# フォント設定（英語で統一して確実に表示）
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
sns.set_style("whitegrid")
print("フォント設定: 英語表示（DejaVu Sans）で統一しました")

def create_output_directory(output_dir):
    """
    出力ディレクトリの作成
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"出力ディレクトリを作成しました: {output_dir}")
    else:
        print(f"出力ディレクトリが既に存在します: {output_dir}")

def load_and_preprocess_data(file_path):
    """
    データの読み込みと前処理
    """
    try:
        # まず全てのシート名を確認
        excel_file = pd.ExcelFile(file_path)
        print(f"=== 利用可能なシート ===")
        for sheet in excel_file.sheet_names:
            print(f"- {sheet}")
        
        # 適切なシートを選択
        if 'Valorant用' in excel_file.sheet_names:
            sheet_name = 'Valorant用'
        elif len(excel_file.sheet_names) > 0:
            sheet_name = excel_file.sheet_names[0]  # 最初のシート
        else:
            raise ValueError("読み込み可能なシートが見つかりません")
            
        print(f"使用するシート: {sheet_name}")
        
        # 選択したシートを読み込み
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        
    except Exception as e:
        print(f"シート指定での読み込みに失敗: {e}")
        print("デフォルトシートで読み込みを試行します...")
        df = pd.read_excel(file_path, engine='openpyxl')
    
    print(f"\n=== データの構造確認 ===")
    print(f"データの形状: {df.shape}")
    print(f"列数: {len(df.columns)}")
    print(f"行数: {len(df)}")
    
    # 列名を確認
    print("\n=== 列名確認 ===")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    # 必要な列のみを抽出
    experience_col = 'Valorantのプレイ経験はありますか。'
    
    # 対象の質問番号 (Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q17, Q18)
    target_questions = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q17', 'Q18']
    
    # 正答列を探す（様々なパターンで検索）
    correct_answer_cols = []
    
    # パターン1: "Q1:正答" の形式
    for q_num in target_questions:
        for col in df.columns:
            if col.startswith(q_num) and '正答' in col:
                correct_answer_cols.append(col)
                break
    
    # パターン2: "Q1: 正答" の形式（スペース有り）
    if len(correct_answer_cols) == 0:
        for q_num in target_questions:
            for col in df.columns:
                if col.startswith(q_num + ':') and '正答' in col:
                    correct_answer_cols.append(col)
                    break
    
    # パターン3: より広範囲で検索
    if len(correct_answer_cols) == 0:
        print("標準的な検索で正答列が見つかりませんでした。より広範囲で検索します...")
        for col in df.columns:
            if '正答' in col:
                # 対象の質問番号が含まれているかチェック
                for q_num in target_questions:
                    if q_num in col:
                        correct_answer_cols.append(col)
                        break
    
    print(f"\n=== 対象正答列 ===")
    for col in correct_answer_cols:
        print(f"見つかった正答列: {col}")
    
    print(f"\n対象正答列数: {len(correct_answer_cols)}")
    
    # データクリーニング：2行目（正答と書いてある行）を除外
    df_clean = df[(df['参加者名'].notna()) & (df['参加者名'] != 'ー') & (df['参加者名'] != '正答')].copy()
    
    print(f"クリーニング後の参加者数: {len(df_clean)}")
    
    # 正答データのサンプル確認
    if len(correct_answer_cols) > 0:
        print("\n=== 正答データサンプル ===")
        for col in correct_answer_cols[:3]:  # 最初の3つの正答列のみ表示
            print(f"\n{col}:")
            print(df_clean[col].value_counts())
    
    return df_clean, experience_col, correct_answer_cols

def categorize_experience(df, experience_col):
    """
    プレイ経験を3群に分類
    """
    def map_experience(exp):
        if pd.isna(exp):
            return np.nan
        elif 'ない' in exp or '少しある' in exp:
            return 'ない・少しある'
        elif 'ある程度ある' in exp or 'かなりある' in exp:
            return 'ある程度ある・かなりある'
        elif '非常に多い' in exp:
            return '非常に多い'
        else:
            return np.nan
    
    df['experience_group'] = df[experience_col].apply(map_experience)
    return df

def calculate_accuracy_rates(df, correct_answer_cols):
    """
    各参加者の正答率を計算
    """
    if len(correct_answer_cols) == 0:
        print("警告: 正答列が見つかりませんでした。")
        df['accuracy_rate'] = np.nan
        return df
    
    accuracy_rates = []
    
    for idx, row in df.iterrows():
        correct_count = 0
        total_count = 0
        
        for col in correct_answer_cols:
            if pd.notna(row[col]):
                total_count += 1
                # 様々な形式のTRUE値を処理
                if (row[col] == True or 
                    str(row[col]).upper() == 'TRUE' or 
                    str(row[col]).upper() == 'T' or
                    row[col] == 1):
                    correct_count += 1
        
        if total_count > 0:
            accuracy_rate = (correct_count / total_count) * 100
            accuracy_rates.append(accuracy_rate)
        else:
            accuracy_rates.append(np.nan)
    
    df['accuracy_rate'] = accuracy_rates
    
    # 正答率の統計情報
    valid_rates = [r for r in accuracy_rates if not pd.isna(r)]
    if len(valid_rates) > 0:
        print(f"\n=== 正答率計算結果 ===")
        print(f"正答率の平均: {np.mean(valid_rates):.2f}%")
        print(f"正答率の範囲: {np.min(valid_rates):.2f}% - {np.max(valid_rates):.2f}%")
    
    return df

def perform_statistical_tests(df):
    """
    統計検定の実行
    """
    # 群の順序を固定
    group_order = ['ない・少しある', 'ある程度ある・かなりある', '非常に多い']
    
    # 正答率データが存在しない場合の処理
    if df['accuracy_rate'].isna().all():
        print("=== 統計分析不可 ===")
        print("正答率データが存在しないため、統計分析を実行できません。")
        return {}
    
    # 群ごとのデータを抽出
    groups = df.groupby('experience_group')['accuracy_rate'].apply(list).to_dict()
    
    # 欠損値を除去
    clean_groups = {}
    for group_name, values in groups.items():
        clean_values = [v for v in values if not pd.isna(v)]
        if clean_values:
            clean_groups[group_name] = clean_values
    
    if len(clean_groups) == 0:
        print("警告: 分析可能なデータがありません。")
        return {}
    
    print("=== 記述統計 ===")
    print(df.groupby('experience_group')['accuracy_rate'].describe())
    print("\n")
    
    # 正規性の検定
    print("=== 正規性検定 (Shapiro-Wilk検定) ===")
    for group_name, values in clean_groups.items():
        if len(values) >= 3:
            stat, p_value = shapiro(values)
            print(f"{group_name}: W = {stat:.4f}, p = {p_value:.4f}")
        else:
            print(f"{group_name}: サンプルサイズが小さすぎます (n={len(values)})")
    print("\n")
    
    # 等分散性の検定
    print("=== 等分散性検定 (Levene検定) ===")
    group_values = list(clean_groups.values())
    if len(group_values) >= 2:
        levene_stat, levene_p = levene(*group_values)
        print(f"Levene検定: F = {levene_stat:.4f}, p = {levene_p:.4f}")
    print("\n")
    
    # 一元配置分散分析
    print("=== 一元配置分散分析 (One-way ANOVA) ===")
    if len(group_values) >= 2:
        f_stat, f_p = f_oneway(*group_values)
        print(f"F = {f_stat:.4f}, p = {f_p:.4f}")
        
        # 効果量の計算 (η²)
        all_values = [val for group in group_values for val in group]
        ss_total = sum((x - np.mean(all_values))**2 for x in all_values)
        ss_between = sum(len(group) * (np.mean(group) - np.mean(all_values))**2 for group in group_values)
        eta_squared = ss_between / ss_total
        print(f"効果量 (η²) = {eta_squared:.4f}")
        
        # 多重比較検定（Tukey HSD）
        if f_p < 0.05:
            print(f"\n=== 多重比較検定 (Tukey HSD) ===")
            if STATSMODELS_AVAILABLE:
                print("ANOVAで有意差が見つかったため、どの群同士に差があるかを検定します。")
                
                # データを多重比較用に準備
                tukey_data = []
                tukey_groups = []
                
                for group_name in clean_groups.keys():
                    for value in clean_groups[group_name]:
                        tukey_data.append(value)
                        tukey_groups.append(group_name)
                
                try:
                    # Tukey HSD検定
                    tukey_results = pairwise_tukeyhsd(tukey_data, tukey_groups, alpha=0.05)
                    print(tukey_results)
                    
                    # 結果の解釈
                    print(f"\n=== 多重比較結果の解釈 ===")
                    summary = str(tukey_results).split('\n')
                    for line in summary:
                        if '---' not in line and len(line.strip()) > 0:
                            parts = line.split()
                            if len(parts) >= 7 and parts[-1] in ['True', 'False']:
                                group1 = parts[0]
                                group2 = parts[1]
                                p_adj = parts[3]
                                reject = parts[-1]
                                
                                if reject == 'True':
                                    print(f"✓ {group1} vs {group2}: 有意差あり (p = {p_adj})")
                                else:
                                    print(f"✗ {group1} vs {group2}: 有意差なし (p = {p_adj})")
                                    
                except Exception as e:
                    print(f"Tukey HSD検定でエラーが発生: {e}")
                    print("代替として各群の平均値を比較します:")
                    _show_mean_comparison(clean_groups, group_order)
            else:
                print("statsmodelsが利用できないため、各群の平均値を比較します:")
                _show_mean_comparison(clean_groups, group_order)
    print("\n")
    
    # Kruskal-Wallis検定（ノンパラメトリック）
    print("=== Kruskal-Wallis検定 (ノンパラメトリック) ===")
    if len(group_values) >= 2:
        h_stat, h_p = kruskal(*group_values)
        print(f"H = {h_stat:.4f}, p = {h_p:.4f}")
    print("\n")
    
    return clean_groups

def _show_mean_comparison(clean_groups, group_order):
    """
    平均値の比較を表示する補助関数
    """
    group_means = {}
    for group_name in clean_groups.keys():
        group_means[group_name] = np.mean(clean_groups[group_name])
    
    print("群の平均値:")
    for group_name in group_order:
        if group_name in group_means:
            print(f"  {group_name}: {group_means[group_name]:.2f}%")
    
    print("\n目視での差の大きさ:")
    groups_list = [g for g in group_order if g in group_means]
    for i in range(len(groups_list)):
        for j in range(i+1, len(groups_list)):
            diff = abs(group_means[groups_list[i]] - group_means[groups_list[j]])
            print(f"  {groups_list[i]} vs {groups_list[j]}: {diff:.2f}%の差")
            
    print("\n推定される有意差（目安）:")
    print("  差が15%以上: おそらく有意差あり")
    print("  差が5%未満: おそらく有意差なし")

def save_statistical_results(df, clean_groups, output_dir):
    """
    統計結果をExcelファイルに保存
    """
    # 群の順序を固定
    group_order = ['ない・少しある', 'ある程度ある・かなりある', '非常に多い']
    
    excel_file = os.path.join(output_dir, 'valorant_statistical_analysis_results.xlsx')
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 1. 個人別データ（群の順序を保持）
        result_df = df[['参加者名', 'experience_group', 'accuracy_rate']].copy()
        # 群の順序でソート
        result_df['group_order'] = result_df['experience_group'].map({group: i for i, group in enumerate(group_order)})
        result_df = result_df.sort_values('group_order').drop('group_order', axis=1)
        result_df.to_excel(writer, sheet_name='個人別データ', index=False)
        
        # 2. 群別サンプルサイズ（指定順序で出力）
        group_counts_data = []
        for group in group_order:
            count = df['experience_group'].value_counts().get(group, 0)
            group_counts_data.append({'経験レベル': group, '人数': count})
        group_counts = pd.DataFrame(group_counts_data)
        group_counts.to_excel(writer, sheet_name='群別サンプルサイズ', index=False)
        
        # 3. 記述統計（指定順序で出力）
        if not df['accuracy_rate'].isna().all():
            desc_stats_data = []
            for group in group_order:
                group_data = df[df['experience_group'] == group]['accuracy_rate']
                if len(group_data) > 0:
                    desc = group_data.describe()
                    desc_stats_data.append({
                        'experience_group': group,
                        'count': desc['count'],
                        'mean': desc['mean'],
                        'std': desc['std'],
                        'min': desc['min'],
                        '25%': desc['25%'],
                        '50%': desc['50%'],
                        '75%': desc['75%'],
                        'max': desc['max']
                    })
            
            if desc_stats_data:
                desc_stats_df = pd.DataFrame(desc_stats_data)
                desc_stats_df.set_index('experience_group').to_excel(writer, sheet_name='記述統計')
        
        # 4. 群別詳細データ（指定順序で出力）
        if len(clean_groups) > 0:
            group_details = []
            for group_name in group_order:
                if group_name in clean_groups:
                    values = clean_groups[group_name]
                    for i, value in enumerate(values):
                        group_details.append({
                            'グループ': group_name,
                            '参加者番号': i+1,
                            '正答率': value
                        })
            
            if group_details:
                group_df = pd.DataFrame(group_details)
                group_df.to_excel(writer, sheet_name='群別詳細データ', index=False)
        
        # 5. 統計検定結果
        if len(clean_groups) > 0:
            stat_results = []
            
            # 正規性検定（指定順序で出力）
            for group_name in group_order:
                if group_name in clean_groups:
                    values = clean_groups[group_name]
                    if len(values) >= 3:
                        stat, p_value = shapiro(values)
                        stat_results.append({
                            '検定': 'Shapiro-Wilk (正規性)',
                            'グループ': group_name,
                            '統計量': stat,
                            'p値': p_value,
                            '結果': '正規分布に従う' if p_value > 0.05 else '正規分布に従わない'
                        })
            
            # 等分散性検定
            group_values = [clean_groups[group] for group in group_order if group in clean_groups]
            if len(group_values) >= 2:
                levene_stat, levene_p = levene(*group_values)
                stat_results.append({
                    '検定': 'Levene (等分散性)',
                    'グループ': '全体',
                    '統計量': levene_stat,
                    'p値': levene_p,
                    '結果': '等分散' if levene_p > 0.05 else '等分散でない'
                })
            
            # 一元配置分散分析と多重比較
            if len(group_values) >= 2:
                f_stat, f_p = f_oneway(*group_values)
                # 効果量計算
                all_values = [val for group in group_values for val in group]
                ss_total = sum((x - np.mean(all_values))**2 for x in all_values)
                ss_between = sum(len(group) * (np.mean(group) - np.mean(all_values))**2 for group in group_values)
                eta_squared = ss_between / ss_total
                
                stat_results.append({
                    '検定': 'One-way ANOVA',
                    'グループ': '全体',
                    '統計量': f_stat,
                    'p値': f_p,
                    '結果': '群間に有意差あり' if f_p < 0.05 else '群間に有意差なし',
                    '効果量(η²)': eta_squared
                })
                
                # 多重比較検定
                if f_p < 0.05 and STATSMODELS_AVAILABLE:
                    try:
                        # データを多重比較用に準備（順序を保持）
                        tukey_data = []
                        tukey_groups = []
                        
                        for group_name in group_order:
                            if group_name in clean_groups:
                                for value in clean_groups[group_name]:
                                    tukey_data.append(value)
                                    tukey_groups.append(group_name)
                        
                        # Tukey HSD検定
                        tukey_results = pairwise_tukeyhsd(tukey_data, tukey_groups, alpha=0.05)
                        
                        # 結果をデータフレームに変換
                        tukey_summary = str(tukey_results).split('\n')
                        for line in tukey_summary:
                            if '---' not in line and len(line.strip()) > 0:
                                parts = line.split()
                                if len(parts) >= 7 and parts[-1] in ['True', 'False']:
                                    group1 = parts[0]
                                    group2 = parts[1]
                                    meandiff = parts[2]
                                    p_adj = parts[3]
                                    reject = parts[-1]
                                    
                                    try:
                                        p_value = float(p_adj)
                                        stat_results.append({
                                            '検定': 'Tukey HSD (多重比較)',
                                            'グループ': f'{group1} vs {group2}',
                                            '統計量': f'平均差: {meandiff}',
                                            'p値': p_value,
                                            '結果': '有意差あり' if reject == 'True' else '有意差なし'
                                        })
                                    except ValueError:
                                        pass
                                    
                    except Exception as e:
                        stat_results.append({
                            '検定': 'Tukey HSD (多重比較)',
                            'グループ': '全体',
                            '統計量': 'エラー',
                            'p値': np.nan,
                            '結果': f'検定実行エラー: {str(e)}'
                        })
                elif f_p < 0.05:
                    # statsmodelsが利用できない場合の代替情報
                    group_means = {name: np.mean(values) for name, values in clean_groups.items()}
                    stat_results.append({
                        '検定': '多重比較 (参考情報)',
                        'グループ': '平均値比較',
                        '統計量': 'statsmodels未インストール',
                        'p値': np.nan,
                        '結果': 'pip install statsmodels で詳細な多重比較が可能'
                    })
            
            # Kruskal-Wallis検定
            if len(group_values) >= 2:
                h_stat, h_p = kruskal(*group_values)
                stat_results.append({
                    '検定': 'Kruskal-Wallis',
                    'グループ': '全体',
                    '統計量': h_stat,
                    'p値': h_p,
                    '結果': '群間に有意差あり' if h_p < 0.05 else '群間に有意差なし'
                })
            
            if stat_results:
                stat_df = pd.DataFrame(stat_results)
                stat_df.to_excel(writer, sheet_name='統計検定結果', index=False)
    
    print(f"統計結果を保存しました: {excel_file}")
    return excel_file

def get_significance_symbol(p_value):
    """
    p値に基づいて有意性のアスタリスクを返す
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return ''

def perform_pairwise_comparisons(clean_groups, group_order):
    """
    多重比較の結果から群間の有意差情報を取得
    """
    if not STATSMODELS_AVAILABLE or len(clean_groups) < 2:
        return {}
    
    try:
        # データを多重比較用に準備
        tukey_data = []
        tukey_groups = []
        
        for group_name in clean_groups.keys():
            for value in clean_groups[group_name]:
                tukey_data.append(value)
                tukey_groups.append(group_name)
        
        # Tukey HSD検定
        tukey_results = pairwise_tukeyhsd(tukey_data, tukey_groups, alpha=0.05)
        
        # 結果を辞書として保存
        pairwise_results = {}
        summary = str(tukey_results).split('\n')
        for line in summary:
            if '---' not in line and len(line.strip()) > 0:
                parts = line.split()
                if len(parts) >= 7 and parts[-1] in ['True', 'False']:
                    group1 = parts[0]
                    group2 = parts[1]
                    p_adj = float(parts[3])
                    reject = parts[-1] == 'True'
                    
                    pairwise_results[f"{group1}_vs_{group2}"] = {
                        'p_value': p_adj,
                        'significant': reject,
                        'symbol': get_significance_symbol(p_adj) if reject else ''
                    }
        
        return pairwise_results
        
    except Exception as e:
        print(f"多重比較でエラー: {e}")
        return {}

def create_visualizations(df, clean_groups, output_dir):
    """
    可視化の作成と保存（棒グラフのみ）
    """
    # データが存在しない場合のチェック
    if len(clean_groups) == 0 or df['accuracy_rate'].isna().all():
        print("警告: 可視化するデータがありません。")
        return
    
    # 群の順序を固定
    group_order = ['ない・少しある', 'ある程度ある・かなりある', '非常に多い']
    
    # 多重比較の結果を取得
    pairwise_results = perform_pairwise_comparisons(clean_groups, group_order)
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # 英語タイトルで統一（確実に表示される）
    title = 'Mean Accuracy Rate by Experience Level'
    xlabel = 'Experience Level'
    ylabel = 'Mean Accuracy Rate (%)'
    
    # 群名の英語対応
    group_labels = {
        'ない・少しある': 'None/Little',
        'ある程度ある・かなりある': 'Moderate/Much', 
        '非常に多い': 'Very Much'
    }
    
    # 平均値の比較（順序を保持、有意差のアスタリスク付き）
    if len(clean_groups) > 0:
        # 順序に従って統計値を計算
        ordered_means = []
        ordered_stds = []
        ordered_labels = []
        
        for group_name in group_order:
            if group_name in clean_groups:
                values = clean_groups[group_name]
                ordered_means.append(np.mean(values))
                ordered_stds.append(np.std(values, ddof=1))
                ordered_labels.append(group_labels.get(group_name, group_name))
        
        x_pos = range(len(ordered_means))
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        bars = ax.bar(x_pos, ordered_means, yerr=ordered_stds, capsize=5, alpha=0.8,
                      color=colors[:len(ordered_means)], edgecolor='white', linewidth=1)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(ordered_labels)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # 各バーの上に値を表示
        for i, (mean, std) in enumerate(zip(ordered_means, ordered_stds)):
            ax.text(i, mean + std + 2, f'{mean:.1f}%', ha='center', va='bottom', 
                    fontweight='bold', fontsize=10)
        
        # 有意差のアスタリスクを追加
        if pairwise_results:
            # グラフの現在の最大値を取得
            current_y_max = max([m + s for m, s in zip(ordered_means, ordered_stds)])
            
            # None/Little vs Very Much の有意差を表示
            key1 = 'ない・少しある_vs_非常に多い'
            key2 = '非常に多い_vs_ない・少しある'  # 順序が逆の場合もチェック
            
            significance_info = None
            if key1 in pairwise_results:
                significance_info = pairwise_results[key1]
            elif key2 in pairwise_results:
                significance_info = pairwise_results[key2]
            
            if significance_info and significance_info['significant']:
                # アスタリスクの位置を調整（グラフ内に収める）
                y_line = current_y_max + 5
                ax.plot([0, 2], [y_line, y_line], 'k-', linewidth=1)
                ax.plot([0, 0], [y_line-2, y_line], 'k-', linewidth=1)
                ax.plot([2, 2], [y_line-2, y_line], 'k-', linewidth=1)
                ax.text(1, y_line + 2, significance_info['symbol'], ha='center', va='bottom',
                        fontsize=14, fontweight='bold')
                
                # Y軸の範囲を調整してアスタリスクが見えるようにする
                ax.set_ylim(0, y_line + 10)
        
        # 統計情報を追加
        ax.text(0.02, 0.98, f'p < 0.05 (ANOVA)', transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # 図を保存
    plot_file = os.path.join(output_dir, 'valorant_visualization_plots.png')
    plt.savefig(plot_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"可視化を保存しました: {plot_file}")
    
    plt.show()

def main():
    """
    メイン関数
    """
    print("=== Valorant実験データ分析 ===\n")
    
    # フォルダとファイルパスの設定
    data_folder = "pilot_experiment_data"
    input_dir = os.path.join(data_folder, "input")
    output_dir = os.path.join(data_folder, "output")
    input_file = os.path.join(input_dir, "pilot_experiment_merged.xlsx")
    
    # 入力ディレクトリの確認
    if not os.path.exists(input_dir):
        print(f"エラー: 入力ディレクトリが存在しません: {input_dir}")
        return None, None
    
    if not os.path.exists(input_file):
        print(f"エラー: 入力ファイルが存在しません: {input_file}")
        return None, None
    
    # 出力ディレクトリの作成
    create_output_directory(output_dir)
    
    # データの読み込みと前処理
    df, experience_col, correct_answer_cols = load_and_preprocess_data(input_file)
    print(f"データ読み込み完了: {len(df)}名の参加者")
    print(f"分析対象の質問数: {len(correct_answer_cols)}")
    
    # 経験レベルの分類
    df = categorize_experience(df, experience_col)
    
    # 群ごとのサンプルサイズ確認
    print("\n=== 群別サンプルサイズ ===")
    group_counts = df['experience_group'].value_counts()
    print(group_counts)
    print("\n")
    
    # 正答率の計算
    df = calculate_accuracy_rates(df, correct_answer_cols)
    
    # 統計検定の実行
    clean_groups = perform_statistical_tests(df)
    
    # 結果をExcelファイルに保存
    excel_file = save_statistical_results(df, clean_groups, output_dir)
    
    # 可視化の作成と保存
    create_visualizations(df, clean_groups, output_dir)
    
    print(f"\n=== 分析完了 ===")
    print(f"入力ファイル: {input_file}")
    print(f"結果保存先: {output_dir}")
    print("出力ファイル:")
    print(f"1. 統計分析結果: {os.path.join(output_dir, 'valorant_statistical_analysis_results.xlsx')}")
    print(f"2. 可視化: {os.path.join(output_dir, 'valorant_visualization_plots.png')}")
    
    return df, clean_groups

# 使用例
if __name__ == "__main__":
    try:
        df, clean_groups = main()
        print("\n=== 分析内容 ===")
        print("1. 記述統計: 各群の平均正答率と標準偏差")
        print("2. 正規性検定: 各群のデータの正規性")
        print("3. 等分散性検定: 群間の分散の等質性")
        print("4. 一元配置分散分析: 群間の平均値の差")
        print("5. Kruskal-Wallis検定: ノンパラメトリック検定")
        print("6. 可視化: 箱ひげ図、バイオリンプロット等")
        print("7. Excel出力: 複数シートでの詳細結果")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("以下を確認してください:")
        print("1. pilot_experiment_data/inputフォルダが存在するか")
        print("2. pilot_experiment_data/input/pilot_experiment_merged.xlsxファイルが存在するか")
        print("3. 必要なライブラリがインストールされているか")
        print("   pip install pandas numpy scipy matplotlib seaborn openpyxl statsmodels")