'use client';

import React from 'react'
import Link from 'next/link';
import { useEffect, useRef ,useState} from 'react';
import { useRouter } from 'next/navigation';
import styles from '../../../css/Tutorial.module.css';

export default function page() {
    const router = useRouter();
    // ★★★ 「認証チェックが完了したか」を記憶する useRef ★★★
    const hasChecked = useRef(false);
    // ★★★ ページを表示して良いか、を決定する useState ★★★
    const [isVerified, setIsVerified] = useState(false);

    useEffect(() => {
        // このuseEffectは2回実行されるが、中の処理は1回しか通らないようにする
        if (!hasChecked.current) {
            // 処理を一度実行した、という印を付ける
            hasChecked.current = true;

            const isRegistrationComplete = sessionStorage.getItem('hanten_registration_complete');

            if (isRegistrationComplete) {
                // 認証OKなら、すぐに値を削除して、表示を許可する
                sessionStorage.removeItem('hanten_registration_complete');
                setIsVerified(true);
            } else {
                // 認証NGなら、リダイレクト
                router.replace('/debates'); // replaceを使うことで、ブラウザの履歴に残らないようにする
            }
        }
    }, [router]); // 依存配列はrouterのまま

    // 認証が完了していない間は、何も表示しない
    if (!isVerified) {
        return null; // または <div>認証を確認中...</div>
    }

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>登録完了！</h1>
                <div className={styles.explainContent}>
                    <p>Hantenへようこそ！</p>
                    <p>
                        ここでは、あなたの意見を深めるための「リバース・ディベート」を楽しむことができます。
                    </p>
                    <p>準備はいいですか？</p>
                </div>
                <Link href="/debates" className={styles.startButton}>
                    Let's Start!
                </Link>
            </div>
        </div>
    )
}
