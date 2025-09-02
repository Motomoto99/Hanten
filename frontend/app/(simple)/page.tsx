import Link from "next/link";
import styles from '@/app/css/Home.module.css';

export default function Home() {
  return (
    <div className={styles.container}>
      <main className={styles.main}>
        {/* --- キャッチコピー --- */}
        <h1 className={styles.title}>
          反対意見が、<span className={styles.highlight}>あなた</span>を強くする。
        </h1>
        <p className={styles.subtitle}>
          ようこそ、リバースディベートアプリ「Hanten」へ。
        </p>

        {/* --- アプリの目的 --- */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>このアプリの目的</h2>
          <p>
            「Hanten」は、ただ勝ち負けを競うディベートアプリではありません。あえて『反対の立場』から議論をすることで、自分では思いもよらなかった視点を発見し、思考を深め、より客観的で、しなやかな知性を育むための「知性のジム」です。
          </p>
        </section>

        {/* --- リバースディベートとは？ --- */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>リバースディベートとは？</h2>
          <p>
            あなたが「賛成」と思うテーマに対して、あなたは「反対派」として議論に参加します。相手の意見を尊重し、その論理を理解しようと努めることで、感情的な対立ではなく、建設的な対話が生まれます。
          </p>
        </section>

        {/* --- 主な機能 --- */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>主な機能</h2>
          <div className={styles.features}>
            <div className={styles.featureCard}>
              <h3>ディベート機能</h3>
              <p>政治の様々なテーマのディベートに参加し、リアルタイムで他のユーザーと意見を交換できます。</p>
            </div>
            <div className={styles.featureCard}>
              <h3>AIによる評価機能</h3>
              <p>終了したディベートは、AIがあなたの議論を客観的に分析し、思考の癖や、より良くするためのヒントを、あなただけにフィードバックします。</p>
            </div>
          </div>
        </section>

        {/* --- 行動喚起 (Call to Action) --- */}
        <section className={styles.ctaSection}>
          <h2 className={styles.ctaTitle}>さあ、新しい知性の扉を開こう</h2>
          <div className={styles.ctaButtons}>
            <Link href={'/sign-up'} className={styles.signUpButton}>
              無料でサインアップ
            </Link>
            <Link href={'/sign-in'} className={styles.signInLink}>
              既にアカウントをお持ちですか？
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
