'use client'

import React from 'react'
import { useState, Suspense  } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import styles from '../../css/Tutorial.module.css'; // スタイルをインポート

function TutorialComponent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [userName, setUserName] = useState(searchParams.get('username') || '');
  const [agreements, setAgreements] = useState({
    respect: false,
    learning: false,
    safeSpace: false,
  });

  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target; // チェックボックスの名前と状態を取得
    setAgreements((prev) => ({ ...prev, [name]: checked })); // チェックボックスの状態を更新
  };

  const isAllAgreed = Object.values(agreements).every(Boolean); // 全てのチェックボックスがチェックされているか確認
  const isReady = userName.trim() !== '' && isAllAgreed; // ユーザー名が空でなく、全てのチェックボックスがチェックされているか確認

  const handleSubmit = () => {
    if (isReady) {
      // 確認画面にユーザー名をクエリパラメータとして渡して遷移
      router.push(`/tutorial/check?username=${encodeURIComponent(userName)}`);
    }
  };
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>ようこそ！</h1>
        <p className={styles.description}>ユーザー名を登録してください</p>
        <input
          type="text"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          placeholder="例：ジョウタロウ"
          className={styles.input}
        />

        <div className={styles.agreementBox}>
          <p className={styles.agreementTitle}>
            私は「Hanten」のコミュニティで以下を守ります
          </p>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              name="respect"
              checked={agreements.respect}
              onChange={handleCheckboxChange}
              className={styles.checkbox}
            />
            人格ではなく、意見を尊重します。
          </label>
          <p className={styles.agreementDetail}>
            相手の意見に反論するのは大歓迎ですが、相手の人格や価値観そのものを否定したり馬鹿にした入りするような発言は行いません。
          </p>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              name="learning"
              checked={agreements.learning}
              onChange={handleCheckboxChange}
              className={styles.checkbox}
            />
            勝ち負けよりも、学びを大切にします。
          </label>
          <p className={styles.agreementDetail}>
            相手を論破することが目的ではありません。自分と違う視点を理解し、自分の考えを深めることです。相手の意見から何か一つでも新しい発見を得ようと努めます。
          </p>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              name="safeSpace"
              checked={agreements.safeSpace}
              onChange={handleCheckboxChange}
              className={styles.checkbox}
            />
            安全な「練習場」であることを忘れません。
          </label>
          <p className={styles.agreementDetail}>
            誰もがうまく意見を言えるわけではありません。相手の未熟さを攻めるのではなく、その意図をくみ取り、建設的な対話を続けます。
          </p>
        </div>

        <div className={styles.buttonContainer}>
          <button
            onClick={handleSubmit}
            disabled={!isReady}
            className={styles.confirmButton}
          >
            確認
          </button>
        </div>
      </div>
    </div>
  )
}

// Suspenseでラップしたものをデフォルトエクスポートします
export default function TutorialPage() {
  return (
      <Suspense fallback={<div>読み込み中...</div>}>
          <TutorialComponent />
      </Suspense>
  );
}