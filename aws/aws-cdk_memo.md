
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

## Link集
- https://github.com/cm-tanaka-keisuke/developersio-cdk
    - cdkの構築の流れを基礎から説明しているブログ
- https://tsdoc.org/pages/tags/privateremarks/
    - TSDocについて