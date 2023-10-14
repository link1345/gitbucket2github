# gitbucket2github
Migrate Issues and PullRequests from GitBucket to Github.

## オリジナルとの変更点
- [レート制限](https://docs.github.com/ja/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limiting)が出てくるようになったので、Sleep関数を付け足した

## これは何？
- GitBacketの Issue と Pull Request をそれっぽく GitHub に移行するためのスクリプトです。
- [ブログ記事](https://kwatanabe.hatenablog.jp/entry/2020/10/22/191134)のネタとして作成したものなので、詳細はそちらを参照下さい。

## ライセンス
- [The MIT License](https://opensource.org/licenses/MIT)
