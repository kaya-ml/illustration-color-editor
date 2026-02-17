# illustration-color-editor

主にLINEスタンプ制作を効率化するために製作した、色置換・背景透過ツールです。
利用シーンに合わせて、「デスクトップ版」と「Web版」の2つの形態で提供しています。

## Overview / プロジェクト概要
イラストの特定の色を一括置換したり、背景を透過させたりする作業を、クリック操作だけで完結させます。

## Motivation / 開発の経緯
AIを使ってLINEスタンプ作成に取り組んでいる友人から、「同じキャラクターを出力させても毎回同じ色にならない」という相談を受けました。
既存の無料画像編集ソフトもいくつか試してみましたが、決定的な解決策には至りませんでした。
そこで「絵を描く」のではなく「既存のイラストの色修正」に特化したツールを自作すれば、友人の作業効率を向上出来ると考え製作しました。
当初は自分のPCで作業を代行するために「デスクトップ版」を開発しましたが、技術に詳しくない友人でも修正出来るものにしたいという思いから、環境構築不要でブラウザから利用できる「Web版」も併せて実装しました。

## Execution Environments / 選べる2つの実行環境

### 1. デスクトップ版 (Tkinter)
ローカル環境で動作する、クリエイター向けのツールです。
- **特徴**: 色置換だけでなく背景透過も可能。大量の画像に対する「一括処理機能」も搭載。
- **技術スタック**: Python, OpenCV, Tkinter
- **こだわり**: 日本語パス（フォルダ名に日本語が含まれる場合）でもエラーが出ないよう、バイナリ読み込みによる画像処理を実装しています。

### 2. Web版 (Streamlit / Hugging Face Spaces)
ブラウザ上でインストール不要ですぐに使える手軽なツールです。
- **URL**: [(https://huggingface.co/spaces/creamybrother/illustration-color-editor)]
- **技術スタック**: Python, Streamlit, OpenCV
- **こだわり**: インストール不要で、環境構築などがなくサクッと色置換・背景透過が出来るように作成しました。

## Technical Highlights / 技術的なこだわり
- **FloodFillアルゴリズムの活用**: OpenCVのFloodFillを用い、境界線を判別した精度の高い色置換を実現。
- **ロジックの共通化とUIの書き分け**: 画像処理を行う「コアロジック」は共通化しつつ、GUI（Tkinter）とWeb（Streamlit）という異なるフロントエンドに対応させました。
- **アルファチャンネル（透過）の制御**: PNG画像の透過情報を保持したまま色を塗り替える、あるいは不透明な背景をアルファチャンネルへ変換する処理など、スタンプ制作に不可欠な透過処理をしっかり制御しています。

## Project Structure / 構成
```text
line-stamp-color-editor/
├── desktop_app/           # デスクトップ版 (Tkinter)
│   └── linestump_colorchanger.py
├── web_app/               # Web版 (Hugging Face / Streamlit)
│   ├── app.py
│   ├── README.md          # Hugging Face上で使用したREADME
│   └── requirements.txt
└── README.md              # リポジトリ全体のメインREADME
```

## Tech Stack / 使用技術
- Language: Python 3.10+
- Libraries: OpenCV, NumPy, Pillow, Tkinter, Streamlit
- Platform: Windows (Desktop) / Hugging Face Spaces (Web)

