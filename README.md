# illustration-color-editor

主にLINEスタンプ制作を効率化するために製作した、色置換・背景透過ツールです。
利用シーンに合わせて、「デスクトップ版」と「Web版」の2つの形態で提供しています。

## Overview / プロジェクト概要
イラストの特定の色を一括置換したり、背景を透過させたりする作業を、クリック操作だけで完結させます。

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
- **こだわり**: インストール不要で、プラットフォーム構築などが厳しい方にもサクッと色置換・背景透過が出来るように作成しました。

## 技術的なこだわり
- **FloodFillアルゴリズムの活用**: OpenCVのFloodFillを用い、境界線を判別した精度の高い色置換を実現。
- **クロスプラットフォーム対応**: 異なるUIライブラリ（Tkinter / Streamlit）を用いて、同じロジックを別環境へ移植する実装力を重視しました。

## Project Structure
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
