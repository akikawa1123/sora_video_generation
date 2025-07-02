## Azure OpenAI の Sora を用いた複数のシーンからなる動画の生成
1. base_prompt.md のストーリー概要を設定する
2. base_prompt.md のプロンプトを LLM に入力し、Sora で利用するプロンプトを生成させる 
3. JSON 形式で出力したプロンプトを video_prompt.json として保存する
4. .env.sample の名前を .env に変更する 
4. .env ファイルのパラメータをデプロイした sora のエンドポイントに変更する
5. video_generation.py を実行して動画を生成する
6. 動画の生成が完了したら、生成された動画 (merged_output.mp4) を確認する

