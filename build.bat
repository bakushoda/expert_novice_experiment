@echo off
echo PsychoPy実験のビルドを開始します...

REM 以前のビルドを削除
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 必要なファイルが存在するかチェック
if not exist "experiment.py" (
    echo エラー: experiment.py が見つかりません
    pause
    exit /b 1
)

if not exist "task_config.py" (
    echo エラー: task_config.py が見つかりません
    pause
    exit /b 1
)

REM PyInstallerでビルド
echo ビルド中...
pyinstaller experiment.spec

if %ERRORLEVEL% neq 0 (
    echo ビルドエラーが発生しました
    pause
    exit /b 1
)

echo ビルド完了！
echo 実行ファイルは dist/experiment/ フォルダにあります

REM 必要なファイルをコピー
echo 設定ファイルをコピー中...
copy "task_config.py" "dist\experiment\"
if exist "google_config.py" copy "google_config.py" "dist\experiment\"

REM imagesフォルダがある場合
if exist "images" (
    echo 画像フォルダをコピー中...
    xcopy "images" "dist\experiment\images\" /e /i /h
)

echo 全て完了しました！
echo dist\experiment\experiment.exe を実行してください
pause