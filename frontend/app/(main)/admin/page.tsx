import React from 'react';
import styles from '@/app/css/Admin.module.css';

export default function AdminPage() {
    const adminUrl = process.env.NEXT_PUBLIC_ADMIN_SITE_URL;

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>管理者ページ</h1>
                <p className={styles.description}>
                    下のボタンから、バックエンドの管理サイトに移動できます。
                </p>

                {/* ★★★ Linkではなく、ただの<a>タグを使うのがポイントですわよ ★★★ */}
                <a
                    href={adminUrl}
                    target="_blank" // 新しいタブで開くのが、親切というものですわ
                    rel="noopener noreferrer" // セキュリティのためのおまじないです
                    className={styles.adminButton}
                >
                    管理サイトへ移動
                </a>

                <p className={styles.note}>
                    操作が終わったら、そのタブを閉じて、<br />こちらのタブに戻ってきてください。
                </p>
            </div>
        </div>
    );
}