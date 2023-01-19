
## setup
- https://aws.amazon.com/jp/getting-started/guides/setup-cdk/module-two/
```bash
# install
npm install -g aws-cdk
cdk --version

# bootstrap
cdk bootstrap aws://ACCOUNT-NUMBER/REGION

# make project
mkdir cdk-demo
cd cdk-demo
cdk init --language typescript
```

## Lambdaのエイリアス運用について
- エイリアス/バージョンともにCDKから発行可能
- 初回以降、バージョン発行を行う場合は論理IDの変更が必要
    - 論理IDが変更されないと実質更新できない
        - 関数名以外のパラメータが更新不可なため(https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.CfnVersion.html)
- デフォルトだと更新時に前回のバージョンが削除されてしまう
    - Stack更新時の削除ポリシーの変更が必要
- Function と エイリアス/バージョン間には明示的に依存関係指定が必要

### 運用案
- エイリアスは初回作成のみCDKで実行、以降のバージョンの付け替えは手動で行う
- バージョンはFunction(のパラメータ)が変更された際には自動で論理IDが再発行されるようにしておく
    - バージョンは削除ポリシーを保持(Retain)にしておく
- 運用の流れ(更新時)
    - CDKでLambdaデプロイ(バージョン発行) ⇒ 対象バージョンで動作確認 ⇒ エイリアスに対象バージョンを紐づける

## Contextについて
- ユーザーが指定できる方法は4種類. 以下優先度順.
    - ①```this.node.setContext('key', 'value')``` での指定(Stackクラスでのみ実行可)
        ```typescript
        import * as cdk from 'aws-cdk-lib';
        import { Construct } from 'constructs';

        const app = new cdk.App();
        const stack = new TestStack(app, 'TestStack');
        
        class TestStack extends cdk.Stack {
            constructor(scope: Construct, id: string, props?: cdk.StackProps) {
                this.node.setContext('k', 'v');
            }
        }
        ```
    - ②cdkコマンド実行時の引数指定
    - ③cdk.json 内での指定
    - ④~/.cdk.json 内での指定
- ①について
    - 上書きできるのは Stack 以下の Construct でのみ.
    - ```cdk.App```に対して cdk.json 内で指定済みの値を app.node.setContext で上書きすることはできない.
    - ```cdk.App```を new した際の引数 cdk.AppProps の context を指定しても上書きできない. cdk.json で設定されていない値であれば追加可能.
    - どうしても上書きしたい場合は　```postCliContext``` を使う.ただしコマンド引数も上書きされる.
        ```json
        # cdk.json
        {
            ...
            "context": {
                "stage": "stage-a"
            },
            ...
        }
        ```
        ```typescript
        // typescript
        import * as cdk from 'aws-cdk-lib';

        // --app.node.setContext で上書きすることはできない.----
        const app = new cdk.App();
        console.log(app.node.tryGetContext('stage'));   // stage-a
        // app.node.setContext('stage', 'stage-b');        // Error: Cannot set context after children have been added     
        // app.node.setContext('env', 'env-b')             // cdk.json で指定されていない key でもエラーになる

        // --new した際の引数 cdk.AppProps の context を指定しても上書きできない.----
        const app2 = new cdk.App({ context: { stage: 'stage-c', env: 'env-c' } });
        console.log(app2.node.tryGetContext('stage'));  // stage-a
        console.log(app2.node.tryGetContext('env'));    // env-c

        // --postCliContext で cdk.json, コマンド実行時引数を上書きできる.----
        const app3 = new cdk.App({ psotCliContext: { stage: 'stage-d', env: 'env-d' } });
        console.log(app2.node.tryGetContext('stage'));  // stage-d
        console.log(app2.node.tryGetContext('env'));    // env-c
        ```

## ドリフトと解決
- スタック内のリソースに対してAWSコンソールなどから変更を加えた場合、テンプレートと実際の値に差が生じる
- この差を検出する機能がドリフト
    - すべてのサービスに対応しているわけではない
        - https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html
- AWSコンソールから確認できる
    - 現時点では対応する cdk コマンドはない模様？
- 解決するには2パターンある
    - ①テンプレートを修正し、実態に合わせる
    - ②リソースをテンプレートに合うように修正する
- ①にはさらに２種類ある
    - リソースの再作成が不要な変更 ⇒ 変更したテンプレートをデプロイすればOK
    - リソースの再作成が必要な変更(破壊的な変更) ⇒ 対象のリソースを一度テンプレートから除外(削除ポリシー
    の設定で削除されないようにしておく)し、インポートする
        - 対象のリソースに対して別リソースから参照がある場合はどうするのか？いろいろややこしそう 

## インポート機能について
- (スタックで作っていない)新規リソースを既存スタックに取り込む機能
    - すべてのサービスに対応しているわけではない
        - https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html
- テンプレートの状態にいくつか条件がある
    - ①取り込むリソース以外の差分がない事
        - CDKMetadata を含む. 出力されるように設定していると必ず差分発生するので```cdk.json```の設定で出力抑制しておくのが良い.
            ```json
            "versionReporting": false,
            ```
    - ②取り込むリソースの現状の設定とテンプレートの内容が一致していること
    - ③取り込むリソースに削除ポリシーが明示的に設定されていること(内容は問わない)
- 条件を満たすテンプレートを用意してAWSコンソールからインポート操作が行える
- CDKプロジェクトから実行する場合は ```cdk import ${stack-name}```
    - cdk@2.47.0 時点では import コマンドはまだプレビュー機能で、正式版ではない模様
        ```
        The 'cdk import' feature is currently in preview.
        ```

## Link集
- https://github.com/cm-tanaka-keisuke/developersio-cdk
    - cdkの構築の流れを基礎から説明しているブログ
- https://tsdoc.org/pages/tags/privateremarks/
    - TSDocについて
- https://tech.nri-net.com/entry/how_about_cdk_import
    - cdk import について
- https://dev.classmethod.jp/articles/aws-devday-online-japan-know-how-from-initial-development-to-operation-on-how-to-use-aws-cdk/
    - cdk の俺的ベストプラクティス？
- https://aws.amazon.com/jp/blogs/news/best-practices-for-developing-cloud-applications-with-aws-cdk/
    - cdk 公式ベストプラクティス
- https://logmi.jp/tech/articles/326696
    - リソース名に物理名をつけることに関する考察