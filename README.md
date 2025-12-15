# PDF Processing App Setup Guide

このアプリケーションを実行するには、以下の外部ツールのインストールが必要です。

## 1. Tesseract OCR (テキスト抽出フォールバック用)

OCR機能を使用するために必要です。

1. [UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) にアクセスします。
2. 最新のインストーラー（例: `tesseract-ocr-w64-setup-v5.x.x.xxxx.exe`）をダウンロードします。
3. インストーラーを実行します。
    - **重要**: インストール中に「Additional script data」を展開し、「Japanese script」と「Japanese vertical script」を選択することをお勧めします（日本語認識のため）。
    - インストール先を覚えておいてください（通常 `C:\Program Files\Tesseract-OCR`）。
4. Windowsの環境変数 `PATH` にインストールフォルダを追加するか、コード内のパス設定を修正してください。

## 2. Poppler (PDF画像変換用)

PDFを画像に変換するために必要です。

1. [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) にアクセスします。
2. 最新のReleaseからzipファイルをダウンロードします（例: `Release-xx.xx.xx-0.zip`）。
3. 解凍し、適当な場所に配置します（例: `C:\Program Files\poppler`）。
4. `bin` フォルダ（例: `C:\Program Files\poppler\Library\bin` または `bin`）をWindowsの環境変数 `PATH` に追加してください。

## 3. アプリケーションの実行

```bash
python main.py
```

## 注意事項

- 初回起動時、環境変数を設定した場合はPCの再起動やターミナルの再起動が必要な場合があります。
- エラーが出る場合は、`main.py` 内の `PDFProcessor` 初期化部分でパスを直接指定してください。
