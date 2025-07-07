from psychopy import visual, core, event, data, gui, logging
import random
import os
import pandas as pd
from datetime import datetime
import json
import sys
import psychopy.monitors

# 安全な終了処理関数
def safe_quit(win=None):
    """安全な終了処理"""
    try:
        # PsychoPyのログ機能を無効化
        from psychopy import logging
        logging.flush()
        logging.console.setLevel(logging.CRITICAL)
    except:
        pass
    
    try:
        if win is not None:
            win.close()
    except:
        pass
    
    try:
        import sys
        sys.exit(0)
    except:
        # 最終手段
        import os
        os._exit(0)

# Google Sheets関連のインポート
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    print("Warning: gspread not installed. Google Sheets機能は無効です。")
    GSPREAD_AVAILABLE = False

# 設定ファイルの読み込み
try:
    from task_config import TASKS, TIMING_CONFIG, EXPERIMENT_INFO, GAME_INFO
except ImportError:
    print("Error: task_config.py not found.")
    sys.exit(1)

# Google Cloud認証情報を別ファイルから読み込み
try:
    from google_config import SERVICE_ACCOUNT_INFO, SPREADSHEET_NAME, WORKSHEET_NAME
    GOOGLE_SHEETS_ENABLED = True and GSPREAD_AVAILABLE
except ImportError:
    print("Warning: google_config.py not found. Google Sheets機能は無効です。")
    GOOGLE_SHEETS_ENABLED = False
    SERVICE_ACCOUNT_INFO = None
    SPREADSHEET_NAME = None
    WORKSHEET_NAME = None


class GoogleSheetsConfig:
    """Google Sheets設定クラス"""
    
    def __init__(self):
        self.SERVICE_ACCOUNT_INFO = SERVICE_ACCOUNT_INFO
        self.SPREADSHEET_NAME = SPREADSHEET_NAME
        self.WORKSHEET_NAME = WORKSHEET_NAME


class ExperimentConfig:
    """実験設定クラス"""
    
    def __init__(self):
        # タイミング設定を外部ファイルから読み込み
        self.fixation_duration = TIMING_CONFIG['fixation_duration']
        self.stimulus_duration = TIMING_CONFIG['stimulus_duration'] 
        self.blackout_duration = TIMING_CONFIG['blackout_duration']
        
        # タスク設定を外部ファイルから読み込み
        self.tasks = TASKS
        self.total_tasks = len(self.tasks)


class ExperimentDisplay:
    """実験画面表示クラス"""
    
    def __init__(self, win, display_mode='auto'):
        self.win = win
        self.display_mode = display_mode  # 'fullscreen', '24inch_max', 'auto'
        
        # ディスプレイ情報を一度だけ取得
        self.screen_width = self.win.size[0]
        self.screen_height = self.win.size[1]
        
        # 画像表示スケールを事前計算
        self._calculate_image_scale()
    
    def _calculate_image_scale(self):
        """画像表示スケールを計算"""
        if self.display_mode == 'fullscreen':
            # 常に画面いっぱい
            self.image_scale = 2.0
            print(f"画像表示モード: 画面いっぱい ({self.screen_width}x{self.screen_height})")
            
        elif self.display_mode == '24inch_max':
            # 24インチを上限とする
            reference_width = 2560  # 24インチ 1440pの幅
            if self.screen_width <= reference_width:
                self.image_scale = 2.0
                print(f"画像表示モード: 画面いっぱい ({self.screen_width}x{self.screen_height})")
            else:
                scale_ratio = reference_width / self.screen_width
                self.image_scale = 2.0 * scale_ratio
                print(f"画像表示モード: 24インチ相当 ({self.screen_width}x{self.screen_height}, スケール: {scale_ratio:.2f})")
                
        else:  # 'auto'
            # run_experiment()の窓設定に合わせる
            if self.win.fullscr:
                # フルスクリーンなら画面いっぱい
                self.image_scale = 2.0
                print(f"画像表示モード: フルスクリーン画面いっぱい")
            else:
                # ウィンドウモードなら窓いっぱい
                self.image_scale = 2.0
                print(f"画像表示モード: ウィンドウいっぱい")
    
    def create_text_stim(self, text, height=0.07, color='white', **kwargs):
        """テキスト刺激を作成します。"""
        if 'wrapWidth' not in kwargs:
            kwargs['wrapWidth'] = 1.8
            
        return visual.TextStim(
            self.win,
            text=text,
            height=height,
            color=color,
            font='MS Gothic',
            anchorHoriz='center',
            anchorVert='center',
            **kwargs
        )
    
    def show_fixation(self, duration):
        """注視点を表示"""
        self.win.color = 'grey'
        self.win.flip()
        core.wait(0.1)
        
        fixation = self.create_text_stim(
            text='+',
            height=0.3,
            color='black',
            bold=True,
            wrapWidth=None
        )
        fixation.draw()
        onset = self.win.flip()
        core.wait(duration)
        return onset
    
    def show_image(self, image_path, duration):
        """画像を表示（スケールは初期化時に決定済み）"""
        self.win.color = 'black'
        
        try:
            game_image = visual.ImageStim(
                self.win, 
                image=image_path,
                units='norm'
            )
            
            # 事前計算されたスケールを使用
            game_image.size = (self.image_scale, self.image_scale)
            
            game_image.draw()
            onset = self.win.flip()
            core.wait(duration)
            return onset
            
        except Exception as e:
            print(f"画像読み込みエラー: {image_path}")
            print(f"エラー詳細: {e}")
            return None
    
    def show_blackout(self, duration):
        """ブラックアウトを表示"""
        self.win.color = 'black'
        onset = self.win.flip()
        core.wait(duration)
        return onset


class QuestionInterface:
    """質問インターフェースクラス (選択肢対応版)"""

    def __init__(self, win):
        self.win = win
        self.display = ExperimentDisplay(win)

    def show_questions(self, questions):
        """
        質問画面を表示し、回答を取得します。
        テキスト入力、選択肢、複数選択に対応します。
        """
        answers = []
        self.win.color = 'black'

        for i, question_data in enumerate(questions, 1):
            display_question = question_data['display_text']
            question_type = question_data.get('type', 'text')
            
            if question_type == 'text':
                # テキスト入力（従来の方法）
                answer = self._handle_text_question(display_question, i, len(questions))
                answers.append(answer)
                
            elif question_type == 'choice':
                # 単一選択
                choices = question_data['choices']
                answer = self._handle_choice_question(display_question, choices, i, len(questions))
                answers.append(answer)
                
            elif question_type == 'multiple_choice':
                # 複数選択
                choices = question_data['choices']
                answer = self._handle_multiple_choice_question(display_question, choices, i, len(questions))
                answers.append(answer)

        # 全問回答後の確認画面
        final_text = "回答完了！\n\n入力した回答:\n"
        for i, ans in enumerate(answers, 1):
            final_text += f"{i}. {ans}\n"
        final_text += "\nスペースキーを押して次のタスクに進んでください。"

        final_stim = self.display.create_text_stim(
            text=final_text,
            height=0.04,
            color='lightgreen',
            wrapWidth=1.8
        )

        waiting = True
        while waiting:
            final_stim.draw()
            self.win.flip()
            
            keys = event.getKeys()
            for key in keys:
                if key == 'escape':
                    safe_quit(self.win)
                elif key == 'space':
                    waiting = False
                    break
            
            core.wait(0.01)
        
        return answers

    def _handle_text_question(self, display_question, current_q, total_q):
        """テキスト入力質問を処理"""
        current_text = ""
        
        while True:
            instruction_text = (
                f"質問 {current_q}/{total_q}\n\n"
                f"{display_question}\n\n"
                "英数字で回答を入力してください\n\n"
                "回答: {}\n\n"
                "Enter: 確定 | Backspace: 削除 | ESC: 終了"
            ).format(current_text + "_")
            
            question_stim = self.display.create_text_stim(
                text=instruction_text,
                height=0.05,
                pos=(0, 0),
                wrapWidth=1.8
            )
            
            question_stim.draw()
            self.win.flip()
            
            keys = event.getKeys()
            
            for key in keys:
                if key == 'escape':
                    safe_quit(self.win)
                elif key == 'return':
                    if current_text.strip():
                        return current_text.strip()
                elif key == 'backspace':
                    current_text = current_text[:-1]
                elif key == 'space':
                    current_text += " "
                elif len(key) == 1 and (key.isalnum() or key in ".,!?-()%"):
                    current_text += key
            
            core.wait(0.01)

    def _handle_choice_question(self, display_question, choices, current_q, total_q):
        """単一選択質問を処理"""
        selected_index = 0
        
        while True:
            # 質問と選択肢を表示
            choice_text = f"質問 {current_q}/{total_q}\n\n{display_question}\n\n"
            
            for i, choice in enumerate(choices):
                if i == selected_index:
                    choice_text += f"→ {i+1}. {choice}\n"
                else:
                    choice_text += f"   {i+1}. {choice}\n"
            
            choice_text += "\n↑↓: 選択  Enter: 確定  ESC: 終了"
            
            question_stim = self.display.create_text_stim(
                text=choice_text,
                height=0.05,
                pos=(0, 0),
                wrapWidth=1.8
            )
            
            question_stim.draw()
            self.win.flip()
            
            keys = event.getKeys()
            
            for key in keys:
                if key == 'escape':
                    safe_quit(self.win)
                elif key == 'return':
                    return choices[selected_index]
                elif key == 'up':
                    selected_index = (selected_index - 1) % len(choices)
                elif key == 'down':
                    selected_index = (selected_index + 1) % len(choices)
                elif key.isdigit():
                    # 数字キーで直接選択
                    num = int(key)
                    if 1 <= num <= len(choices):
                        selected_index = num - 1
            
            core.wait(0.01)

    def _handle_multiple_choice_question(self, display_question, choices, current_q, total_q):
        """複数選択質問を処理"""
        selected_indices = []
        current_index = 0
        
        while True:
            # 質問と選択肢を表示
            choice_text = f"質問 {current_q}/{total_q}\n\n{display_question}\n\n"
            
            for i, choice in enumerate(choices):
                marker = "→" if i == current_index else "  "
                check = "✓" if i in selected_indices else " "
                choice_text += f"{marker} [{check}] {i+1}. {choice}\n"
            
            choice_text += "\n↑↓: 移動  Space: 選択/解除  Enter: 確定  ESC: 終了"
            
            question_stim = self.display.create_text_stim(
                text=choice_text,
                height=0.045,
                pos=(0, 0),
                wrapWidth=1.8
            )
            
            question_stim.draw()
            self.win.flip()
            
            keys = event.getKeys()
            
            for key in keys:
                if key == 'escape':
                    safe_quit(self.win)
                elif key == 'return':
                    if selected_indices:
                        selected_choices = [choices[i] for i in sorted(selected_indices)]
                        return "; ".join(selected_choices)
                    else:
                        return "選択なし"
                elif key == 'up':
                    current_index = (current_index - 1) % len(choices)
                elif key == 'down':
                    current_index = (current_index + 1) % len(choices)
                elif key == 'space':
                    if current_index in selected_indices:
                        selected_indices.remove(current_index)
                    else:
                        selected_indices.append(current_index)
            
            core.wait(0.01)


class DataManager:
    """データ管理クラス"""
    
    @staticmethod
    def upload_to_google_sheets(results, participant_info):
        """結果をGoogle Spreadsheetに保存（質問一つにつき一列）"""
        if not GOOGLE_SHEETS_ENABLED:
            print("Google Sheets機能が無効です。")
            return False, None
            
        try:
            sheets_config = GoogleSheetsConfig()
            
            # 認証
            credentials = Credentials.from_service_account_info(
                sheets_config.SERVICE_ACCOUNT_INFO,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            
            # Google Sheets APIクライアント作成
            gc = gspread.authorize(credentials)
            
            # スプレッドシートを開く（存在しない場合は作成）
            try:
                spreadsheet = gc.open(sheets_config.SPREADSHEET_NAME)
            except gspread.SpreadsheetNotFound:
                spreadsheet = gc.create(sheets_config.SPREADSHEET_NAME)
                print(f"新しいスプレッドシートを作成しました: {sheets_config.SPREADSHEET_NAME}")
            
            # ワークシートを取得または作成
            try:
                worksheet = spreadsheet.worksheet(sheets_config.WORKSHEET_NAME)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=sheets_config.WORKSHEET_NAME,
                    rows=1000,
                    cols=100
                )
            
            # 順序を保った質問列の作成（task_configの順序に従う）
            ordered_columns = []
            question_counter = 1
            
            # task_configから直接順序を取得
            from task_config import TASKS
            for task in TASKS:
                for question in task['questions']:
                    spreadsheet_text = question['spreadsheet_text']
                    ordered_columns.append(f"Q{question_counter}: {spreadsheet_text}")
                    question_counter += 1
            
            # データを参加者ごとに1行にまとめる
            participant_row = [participant_info['participant_name']]
            participant_row.append(datetime.now().isoformat())
            
            # 各質問列の値を順番に追加
            for column_header in ordered_columns:
                # "Q1: VALO_味方キャラクター数_低刺激" から "VALO_味方キャラクター数_低刺激" を抽出
                spreadsheet_text = column_header.split(": ", 1)[1]
                
                # 該当する質問の回答を探す
                answer = ""
                for result in results:
                    if spreadsheet_text in result:
                        answer = result[spreadsheet_text]
                        break
                participant_row.append(answer)
            
            # ヘッダーを作成（初回のみ）
            existing_data = worksheet.get_all_values()
            if not existing_data or not existing_data[0]:
                headers = ['参加者名', '実施日時'] + ordered_columns
                worksheet.append_row(headers)
            
            # データ行を追加
            worksheet.append_row(participant_row)
            
            print(f"結果をGoogle Spreadsheetに保存しました")
            print(f"スプレッドシート: {sheets_config.SPREADSHEET_NAME}")
            print(f"URL: {spreadsheet.url}")
            
            return True, spreadsheet.url
            
        except Exception as e:
            print(f"Google Spreadsheetへの保存でエラーが発生しました: {e}")
            return False, None
    
    @staticmethod
    def save_results_locally(results, participant_info):
        """ローカルにCSVファイルとして保存（質問一つにつき一列）"""
        try:
            # resultディレクトリを作成（存在しない場合）
            result_dir = "result"
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{participant_info['participant_name']}_{timestamp}.csv"
            filepath = os.path.join(result_dir, filename)
            
            # データを参加者ごとに1行にまとめる
            row_data = {'参加者名': participant_info['participant_name']}
            row_data['実施日時'] = datetime.now().isoformat()
            
            # 順序を保った質問列の作成（task_configの順序に従う）
            from task_config import TASKS
            question_counter = 1
            
            for task in TASKS:
                for question in task['questions']:
                    spreadsheet_text = question['spreadsheet_text']
                    column_header = f"Q{question_counter}: {spreadsheet_text}"
                    
                    # 該当する質問の回答を探す
                    answer = ""
                    for result in results:
                        if spreadsheet_text in result:
                            answer = result[spreadsheet_text]
                            break
                    
                    row_data[column_header] = answer
                    question_counter += 1
            
            # データフレームを作成
            df = pd.DataFrame([row_data])
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            print(f"ローカルバックアップを保存しました: {filepath}")
            return True, filepath
        except Exception as e:
            print(f"ローカル保存でエラーが発生しました: {e}")
            return False, None


def get_participant_info():
    """参加者名を取得（英数字版）"""
    # まずは英数字での入力を試行
    print("参加者名を英数字で入力してください（例: Tanaka_Taro, Participant01 など）")
    
    dlg = gui.Dlg(title="参加者情報")
    dlg.addField('参加者名（英数字）:', tip='英数字とアンダースコアで入力してください')
    
    dlg.show()
    if dlg.OK and dlg.data[0].strip():
        return {'participant_name': dlg.data[0].strip()}
    else:
        # 再試行またはデフォルト名を使用
        retry_dlg = gui.Dlg(title="参加者名確認")
        retry_dlg.addText("参加者名が入力されていません。")
        retry_dlg.addField("デフォルト名を使用しますか？ (Yes/No):", "Yes")
        retry_dlg.show()
        
        if retry_dlg.OK and retry_dlg.data[0].lower() in ['yes', 'y']:
            from datetime import datetime
            default_name = f"Participant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return {'participant_name': default_name}
        else:
            return get_participant_info()  # 再帰的に再試行


def create_trial_list(config):
    """試行リストを作成"""
    trials = []
    
    # すべてのタスクを1回ずつ使用（順序はそのまま）
    for i, task in enumerate(config.tasks):
        trial = {
            'trial_num': i + 1,
            'task_data': task
        }
        trials.append(trial)
    
    return trials


def get_game_from_image_path(image_path):
    """画像パスからゲーム名を取得"""
    if 'VALO_' in image_path:
        return 'VALO'
    elif 'LOL_' in image_path:
        return 'LOL'
    elif 'FN_' in image_path:
        return 'FN'
    return None


def show_game_transition(win, display, current_game, next_game):
    """ゲーム切り替え画面を表示"""
    if next_game and next_game in GAME_INFO:
        transition_text = f'''ここからは{GAME_INFO[next_game]['display_name']}に関する問題になります。

準備ができたらスペースキーを押してください。'''
        
        transition_msg = display.create_text_stim(
            text=transition_text, 
            height=0.08,
            color='lightblue'
        )
        
        # より安全なキー待機処理
        waiting = True
        while waiting:
            transition_msg.draw()
            win.flip()
            
            keys = event.getKeys()
            for key in keys:
                if key == 'escape':
                    safe_quit(win)
                elif key == 'space':
                    waiting = False
                    break
            core.wait(0.01)


def run_trial(win, trial, config, display, question_interface):
    """1試行（1タスク）を実行"""
    
    # ESCキーでの中断チェック
    if 'escape' in event.getKeys():
        safe_quit(win)
    
    task_data = trial['task_data']
    
    # 1. 黒画面（初期化）
    win.color = 'black'
    win.flip()
    core.wait(0.3)
    
    # 2. 注視点表示
    fixation_onset = display.show_fixation(config.fixation_duration)
    
    # 3. ゲーム画面表示
    stimulus_onset = display.show_image(task_data['image_path'], config.stimulus_duration)
    if stimulus_onset is None:
        return None
    
    # 4. ブラックアウト
    blackout_onset = display.show_blackout(config.blackout_duration)
    
    # 5. 質問回答
    answers = question_interface.show_questions(task_data['questions'])
    
    # 結果をまとめる - 各質問を個別に記録
    result = {
        'trial_num': trial['trial_num'],
        'image_path': task_data['image_path'],
        'fixation_onset': fixation_onset,
        'stimulus_onset': stimulus_onset,
        'blackout_onset': blackout_onset,
        'stimulus_duration_actual': blackout_onset - stimulus_onset,
        'timestamp': datetime.now().isoformat()
    }
    
    # 各質問と回答を個別に記録
    for i, (question, answer) in enumerate(zip(task_data['questions'], answers), 1):
        # spreadsheet_textを使用して列名を設定
        spreadsheet_text = question.get('spreadsheet_text', f'Question_{i}')
        result[spreadsheet_text] = answer
    
    return result


def run_experiment():
    """メイン実験関数"""
    
    # 参加者情報取得
    participant_info = get_participant_info()
    
    # 設定読み込み
    config = ExperimentConfig()
    
    # ディスプレイサイズを取得してウィンドウ設定を決定
    monitor = psychopy.monitors.Monitor('testMonitor')
    screen_size = monitor.getSizePix()
    
    # ディスプレイサイズに応じてウィンドウ設定を決定
    if screen_size[0] >= 1920:  # 大きいディスプレイ（1920px以上）
        window_size = []
        fullscreen_mode = True
        print(f"大きいディスプレイ検出: {screen_size[0]}x{screen_size[1]} - フルスクリーンモードで実行")
    else:  # 小さいディスプレイ（1920px未満）
        window_size = [1470, 956]
        fullscreen_mode = True
        print(f"小さいディスプレイ検出: {screen_size[0]}x{screen_size[1]}")
    
    # ウィンドウ作成
    win = visual.Window(
        size=window_size,
        fullscr=fullscreen_mode,
        color='black',
        units='norm',
        allowGUI=False,
        waitBlanking=True
    )
    
    # マウスカーソルを非表示
    win.mouseVisible = False
    
    # 表示クラスを初期化（画像表示モードを指定）
    display = ExperimentDisplay(win, display_mode='24inch_max')
    question_interface = QuestionInterface(win)
    
    # 試行リスト作成
    trials = create_trial_list(config)
    
    # 実験開始メッセージ
    welcome_text = f'''{EXPERIMENT_INFO['name']}

この実験では、ゲーム画面を見た後に質問に回答していただきます。

タスクの流れ：
1. 注視点（+）を見つめる
2. ゲーム画面が短時間表示される
3. 黒い画面になる
4. 質問に回答する

全部で{config.total_tasks}個のタスクがあります。

注意：
・**普段通りゲームをプレイしているつもりで画面を見てください。**

・注視点が現れたら、画面中央を見つめてください
・途中で止めたい場合は ESC キーを押してください

準備ができたらスペースキーを押して開始してください。'''
    
    welcome_msg = display.create_text_stim(welcome_text, height=0.06)
    
    # より安全なキー待機処理
    waiting = True
    while waiting:
        welcome_msg.draw()
        win.flip()
        
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                safe_quit(win)
            elif key == 'space':
                waiting = False
                break
        core.wait(0.01)
    
    # 結果記録用リスト
    results = []
    
    # ゲーム切り替え管理用変数
    current_game = None
    
    # 各試行を実行
    for i, trial in enumerate(trials):
        # 現在の試行のゲームを取得
        next_game = get_game_from_image_path(trial['task_data']['image_path'])
        
        # ゲームが変わったかチェック
        if current_game != next_game and next_game is not None:
            # ゲーム切り替え画面を表示
            show_game_transition(win, display, current_game, next_game)
            current_game = next_game
        
        # 進捗表示（最初の試行以外）
        if i > 0:
            progress_text = f'''タスク {i+1}/{len(trials)}

準備ができたらスペースキーを押して次のタスクを開始してください。'''
            
            progress_msg = display.create_text_stim(progress_text, height=0.08)
            
            # より安全なキー待機処理
            waiting = True
            while waiting:
                progress_msg.draw()
                win.flip()
                
                keys = event.getKeys()
                for key in keys:
                    if key == 'escape':
                        safe_quit(win)
                    elif key == 'space':
                        waiting = False
                        break
                core.wait(0.01)
        
        # カウントダウン（最初の試行のみ）
        if i == 0:
            for count in [3, 2, 1]:
                countdown = display.create_text_stim(
                    text=str(count),
                    height=0.2,
                    color='white',
                    bold=True
                )
                countdown.draw()
                win.flip()
                core.wait(1.0)
        
        # 試行実行
        result = run_trial(win, trial, config, display, question_interface)
        if result:
            result.update(participant_info)
            results.append(result)
    
    # 実験終了メッセージ
    end_text = '''全てのタスクが終了しました。

ご協力ありがとうございました！

スペースキーを押して終了してください。'''
    
    end_msg = display.create_text_stim(end_text, height=0.08)
    
    # より安全なキー待機処理
    waiting = True
    while waiting:
        end_msg.draw()
        win.flip()
        
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                safe_quit(win)
            elif key == 'space':
                waiting = False
                break
        core.wait(0.01)
    
    # 結果を保存
    print("\n=== 結果を保存中 ===")
    
    # 1. Google Spreadsheetに保存を試行
    sheets_success, sheets_url = DataManager.upload_to_google_sheets(results, participant_info)
    
    # 2. ローカルにバックアップ保存
    local_success, local_filename = DataManager.save_results_locally(results, participant_info)
    
    # 保存結果の表示
    save_status_text = "=== 保存完了 ===\n\n"
    
    if sheets_success:
        save_status_text += "✓ Google Spreadsheetに保存されました\n"
        if sheets_url:
            save_status_text += f"URL: {sheets_url}\n\n"
    else:
        save_status_text += "✗ Google Spreadsheetへの保存に失敗しました\n\n"
    
    if local_success:
        save_status_text += f"✓ ローカルバックアップ: {local_filename}\n\n"
    else:
        save_status_text += "✗ ローカル保存に失敗しました\n\n"
    
    save_status_text += "スペースキーを押して終了してください。"
    
    # 保存結果を画面に表示
    save_status_msg = display.create_text_stim(save_status_text, height=0.06)
    
    # より安全なキー待機処理
    waiting = True
    while waiting:
        save_status_msg.draw()
        win.flip()
        
        keys = event.getKeys()
        for key in keys:
            if key == 'escape':
                core.quit()
            elif key == 'space':
                waiting = False
                break
        core.wait(0.01)
    
    # 基本統計を表示
    print(f"\n=== 実験結果 ===")
    print(f"総タスク数: {len(results)}")
    print(f"参加者名: {participant_info['participant_name']}")
    
    # 保存状況をコンソールに表示
    if sheets_success:
        print(f"Google Spreadsheet保存: 成功")
        if sheets_url:
            print(f"スプレッドシートURL: {sheets_url}")
    else:
        print(f"Google Spreadsheet保存: 失敗")
    
    if local_success:
        print(f"ローカル保存: 成功 ({local_filename})")
    else:
        print(f"ローカル保存: 失敗")
    
    # タイミング精度チェック
    actual_durations = [r['stimulus_duration_actual'] for r in results if r['stimulus_duration_actual'] is not None]
    if actual_durations:
        avg_duration = sum(actual_durations) / len(actual_durations)
        print(f"\n実際の刺激提示時間: 平均 {avg_duration:.4f}秒 (目標: {config.stimulus_duration}秒)")
    
    win.close()
    # core.quit()


if __name__ == '__main__':
    # ログレベル設定（エラー時のデバッグ用）
    logging.console.setLevel(logging.WARNING)
    
    run_experiment()