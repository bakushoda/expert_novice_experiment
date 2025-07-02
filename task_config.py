# 実験メタデータ
EXPERIMENT_INFO = {
    'name': 'リコール課題',
    'description': 'varolant, fortnite, league of legendsを用いたリコール課題'
}

# 実験タイミング設定
TIMING_CONFIG = {
    'fixation_duration': 2.0,  # 注視点表示時間（秒）
    'stimulus_duration': 2.5,    # ゲーム画面表示時間（秒）
    'blackout_duration': 1.5   # ブラックアウト時間（秒）
}

TASKS = [
    {
        'image_path': 'images/VALO_champ_low.png',
        'questions': [
            {
                'display_text': '画面に映っていた味方キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_味方キャラクター数_低刺激',
                'type': 'text'
            },
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_敵キャラクター数_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/VALO_champ_high.png',
        'questions': [
            {
                'display_text': '画面に映っていた味方キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_味方キャラクター数_高刺激',
                'type': 'text'
            },
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_敵キャラクター数_高刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/VALO_champ_low2.png',
        'questions': [
            {
                'display_text': '画面に映っていた味方キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_味方キャラクター数_遠近_低刺激',
                'type': 'text'
            },
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_敵キャラクター数_遠近_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/VALO_champ_high2.png',
        'questions': [
            {
                'display_text': '画面に映っていた味方キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_味方キャラクター数_遠近_高刺激',
                'type': 'text'
            },
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'VALO_敵キャラクター数_遠近_高刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/VALO_skill_low.png',
        'questions': [
            {
                'display_text': 'スキル・エフェクトを見ましたか？',
                'spreadsheet_text': 'VALO_スキル有無_低刺激',
                'type': 'choice',
                'choices': ['はっきりと見えた', '少し見えた', 'ほとんど見えなかった', 'まったく見えなかった']
            },
            {
                'display_text': 'スキル・エフェクトの数はどの程度でしたか？',
                'spreadsheet_text': 'VALO_スキル数_低刺激',
                'type': 'choice',
                'choices': ['0個', '1個', '2-3個', '4-5個', '6個以上', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの色で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'VALO_スキル色_低刺激',
                'type': 'multiple_choice',
                'choices': ['赤系', '青系', '黄色系', '緑系', '紫系', '白/光', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの位置で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'VALO_スキル位置_低刺激',
                'type': 'multiple_choice',
                'choices': ['画面左上', '画面右上', '画面左下', '画面右下', '画面中央', '覚えていない']
            }
        ]
    },
    {
        'image_path': 'images/VALO_skill_high.png',
        'questions': [
            {
                'display_text': 'スキル・エフェクトを見ましたか？',
                'spreadsheet_text': 'VALO_スキル有無_高刺激',
                'type': 'choice',
                'choices': ['はっきりと見えた', '少し見えた', 'ほとんど見えなかった', 'まったく見えなかった']
            },
            {
                'display_text': 'スキル・エフェクトの数はどの程度でしたか？',
                'spreadsheet_text': 'VALO_スキル数_高刺激',
                'type': 'choice',
                'choices': ['0個', '1個', '2-3個', '4-5個', '6個以上', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの色で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'VALO_スキル色_高刺激',
                'type': 'multiple_choice',
                'choices': ['赤系', '青系', '黄色系', '緑系', '紫系', '白/光', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの位置で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'VALO_スキル位置_高刺激',
                'type': 'multiple_choice',
                'choices': ['画面左上', '画面右上', '画面左下', '画面右下', '画面中央', '覚えていない']
            }
        ]
    },
    {
        'image_path': 'images/VALO_minimap_low.png',
        'questions': [
            {
                'display_text': 'ミニマップに映っていたキャラクターアイコンの数を教えてください。',
                'spreadsheet_text': 'VALO_ミニマップキャラクター数_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/VALO_minimap_high.png',
        'questions': [
            {
                'display_text': 'ミニマップに映っていたキャラクターアイコンの数を教えてください。',
                'spreadsheet_text': 'VALO_ミニマップキャラクター数_高刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/LOL_champ_low.jpg',
        'questions': [
            {
                'display_text': '画面に映っていた味方キャラクターの数を教えてください。',
                'spreadsheet_text': 'LOL_味方キャラクター数_低刺激',
                'type': 'text'
            },
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'LOL_敵キャラクター数_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/LOL_champ_high.jpg',
        'questions': [
            {
                'display_text': '画面に映っていた味方キャラクターの数を教えてください。',
                'spreadsheet_text': 'LOL_味方キャラクター数_高刺激',
                'type': 'text'
            },
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'LOL_敵キャラクター数_高刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/LOL_skill_low.jpg',
        'questions': [
            {
                'display_text': 'スキル・エフェクトを見ましたか？',
                'spreadsheet_text': 'LOL_スキル有無_低刺激',
                'type': 'choice',
                'choices': ['はっきりと見えた', '少し見えた', 'ほとんど見えなかった', 'まったく見えなかった']
            },
            {
                'display_text': 'スキル・エフェクトの数はどの程度でしたか？',
                'spreadsheet_text': 'LOL_スキル数_低刺激',
                'type': 'choice',
                'choices': ['0個', '1個', '2-3個', '4-5個', '6個以上', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの色で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'LOL_スキル色_低刺激',
                'type': 'multiple_choice',
                'choices': ['赤系', '青系', '黄色系', '緑系', '紫系', '白/光', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの位置で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'LOL_スキル位置_低刺激',
                'type': 'multiple_choice',
                'choices': ['画面左上', '画面右上', '画面左下', '画面右下', '画面中央', '覚えていない']
            }
        ]
    },
    {
        'image_path': 'images/LOL_skill_high.jpg',
        'questions': [
            {
                'display_text': 'スキル・エフェクトを見ましたか？',
                'spreadsheet_text': 'LOL_スキル有無_高刺激',
                'type': 'choice',
                'choices': ['はっきりと見えた', '少し見えた', 'ほとんど見えなかった', 'まったく見えなかった']
            },
            {
                'display_text': 'スキル・エフェクトの数はどの程度でしたか？',
                'spreadsheet_text': 'LOL_スキル数_高刺激',
                'type': 'choice',
                'choices': ['0個', '1個', '2-3個', '4-5個', '6個以上', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの色で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'LOL_スキル色_高刺激',
                'type': 'multiple_choice',
                'choices': ['赤系', '青系', '黄色系', '緑系', '紫系', '白/光', '覚えていない']
            },
            {
                'display_text': 'スキル・エフェクトの位置で覚えているものは？（複数選択可）',
                'spreadsheet_text': 'LOL_スキル位置_高刺激',
                'type': 'multiple_choice',
                'choices': ['画面左上', '画面右上', '画面左下', '画面右下', '画面中央', '覚えていない']
            }
        ]
    },
    {
        'image_path': 'images/LOL_health_low.jpg',
        'questions': [
            {
                'display_text': '緑色のHPバーのキャラクターのヘルスは何％ぐらいでしたか？',
                'spreadsheet_text': 'LOL_HP_低刺激',
                'type': 'choice',
                'choices': ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%', '覚えていない']
            }
        ]
    },
    {
        'image_path': 'images/LOL_health_high.jpg',
        'questions': [
            {
                'display_text': '緑色のHPバーのキャラクターのヘルスは何％ぐらいでしたか？',
                'spreadsheet_text': 'LOL_HP_高刺激',
                'type': 'choice',
                'choices': ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%', '覚えていない']
            }
        ]
    },
    {
        'image_path': 'images/LOL_minimap_low.jpg',
        'questions': [
            {
                'display_text': 'ミニマップに映っていたキャラクターアイコンの数を教えてください。',
                'spreadsheet_text': 'LOL_ミニマップキャラクター数_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/LOL_minimap_high.jpg',
        'questions': [
            {
                'display_text': 'ミニマップに映っていたキャラクターアイコンの数を教えてください。',
                'spreadsheet_text': 'LOL_ミニマップキャラクター数_高刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/FN_champ_low.png',
        'questions': [
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'FN_敵キャラクター数_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/FN_champ_high.png',
        'questions': [
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'FN_敵キャラクター数_高刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/FN_champ_low2.png',
        'questions': [
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'FN_敵キャラクター数_遠近_低刺激',
                'type': 'text'
            }
        ]
    },
    {
        'image_path': 'images/FN_champ_high2.png',
        'questions': [
            {
                'display_text': '画面に映っていた敵キャラクターの数を教えてください。',
                'spreadsheet_text': 'FN_敵キャラクター数_遠近_高刺激',
                'type': 'text'
            }
        ]
    }
]