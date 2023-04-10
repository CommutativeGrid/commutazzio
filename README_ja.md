# Commutative Ladder Source-Sink Interval Approximation

**C**ommutative **la**dder **s**ource-**s**ink **i**nterval **a**pproximationは、任意の長さの可換ラダーのソースシンク型区間近似を計算するための統合的な計算ツールを提供するPythonモジュールである。
fcc/hcp格子のパラメータ入力から、装飾されたパーシスタンスダイアグラムまで、合理的に処理することができるのが特徴である。

このモジュールを円滑に利用するためには、作業ディレクトリに [random-cech](https://bitbucket.org/tda-homcloud/random-cech/src/master/) をインストールする必要があります。詳しくは[以下](##基本的な使い方)をご覧下さい。


Using this module smoothly requires the installation of [random-cech](https://bitbucket.org/tda-homcloud/random-cech/src/master/) in the working directory. See [below](##Basic-usage) for details.

## インストール

このモジュールをインストールするには、`python3.9`が必要です。

```
git clone https://github.com/Commutative-Ladder/classia.git
```
で、クローンされたフォーラに `cd` を適用します。
```
pip install .
```

アップグレードするには、以下を実行します。
```
pip install . --upgrade
```

### 開発(編集)モードでのインストールについて

```
pip install -e .
```

## Basic usage

## 基本的な使い方

実行のたびに多くのファイルが生成されるので、新しいフォルダを作業ディレクトリとして作成することをお勧めします。作業ディレクトリのサブフォルダに [random-cech](https://bitbucket.org/tda-homcloud/random-cech/src/master/) をインストールすることをお勧めします。そうでなければ、引数 `executor` に実行ファイル `cech_filtration` の場所を指定する必要があります。

実行時には、中間データを格納するために `point_cloud` と `filtration` という名前のディレクトリが生成される。

また、ネイティブのJavascriptを使用して持続性ダイアグラムを作成するために、`samples` にある `css` と `js` フォルダを作業ディレクトリにコピーしておく必要がある。ただし、`plotly`だけを使用する場合は、この作業は必要ない。

最後に、作業ディレクトリは以下のような構成になります。

```
dir
|
+--random-cech
|
+--point_cloud
|
+--filtration
|
+--css
|
+--js
```

### CLI経由

このように多くのパラメータがありますが、補償としてより多くのカスタマイズが可能です。以下に例を挙げ、各パラメータの詳細を説明する。

シェル
python -m classia --crystal_type "fcc" --start 1 --end 6 --survival_rates "[0.5, 1]" --dim 1 --lattice_layer_size 5 --ladder_length 10 plot --title "test_from_cli" --file "./ttt.html" --overwrite "False"
```

* `crystal_type`: 原子の半径を1とした格子データを作成する。以下の値のいずれかを指定します。
  * `fcc`: 面心立方(face centerd cubic)。
  * `hcp`: 六方最密充填(hexagonal close packing).
* `start`: Čech 複合体の開始半径。
* `end`: 中間値は `ladder_length` に従って線形に補間されます。
* `survival_rates`: 下の行と上の行の生存率をそれぞれ指定する2つの値を持つリスト．
* `dim`: 使用するホモロジー次元
* `lattice_layer_size`: 1つの座標に沿った原子の数。合計で `lattice_layer_size**3` 個の原子が存在することになる。
* `ladder_length`: 可換ラダーの長さ。CL(50)の場合、入力は50である。

以上のパラメータが入力データである。次に、計算エンジンが動作し、出力は接続された持続性ダイアグラムをプロットするために使用されます。コマンドラインの `plot` の後のパラメータは出力を指定する。

* `title`: ダイアグラムのタイトル。無視することもできる。
* `file`: 生成される html ファイルのファイルパス。無視してもかまいません。
* `overwrite`: 同じ名前のファイルが存在する場合、上書きするかどうか。False` に設定し、 `file` を指定しなかった場合、ランダムなファイル名が使用される。もし `True` に設定し、かつ `file` を指定しなかった場合は、 `./test.html` が使用されます。

### Pythonスクリプトを実行する場合

使用例は `./samples/compute_and_save.py` と `./samples/load_and_plot.py` で紹介されています。計算には非常に時間がかかるので、結果をファイルに保存しておき、後で使用したり、プロットスタイルを変更したりすることをお勧めします。

### Javascriptのネイティブメソッド

CLIを使用したJavascriptのネイティブメソッドでは、`plot`を`plot_js`に置き換えて、以下のパラメータを指定しない。例
例: ``shell
python -m classia --crystal_type "fcc" --start 1 --end 6 --survival_rates "[0.5, 1]" --dim 1 --lattice_layer_size 5 --ladder_length 10 plot_js
```

pythonスクリプトを使用する場合も同様です。

どちらの方法でも、`fcc_7_0.5_1_50.js`のようなファイル名の新しいJavascripteファイルが作成されます。./samples/visualization.html` を作業ディレクトリにコピーし、11行目のソースをそのファイル名に変更します。

### ホスト

生成された `html` ファイルを直接開くことも可能ですが、作業ディレクトリで以下のコマンドを実行するなど、単純な localhost を使用することをお勧めします。

```python
python -m http.server 8000
```
そして、ブラウザで`http://localhost:8000/`を開いてください。

## 問題点

cdn経由で `plotly.js` ライブラリを読み込むには、インターネット接続が必要です。オフラインで作業したい場合は、CLIの最後に `--include_plotlyjs 'True'` を渡すか、プロット中にPythonスクリプトで追加してください。