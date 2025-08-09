'use client';

import React from 'react'
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import axios from 'axios';
import { Suspense } from 'react';
import styles from '../../../css/Tutorial.module.css';

function CheckComponent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const userName = searchParams.get('username');
    const { getToken } = useAuth();

    const handleRegister = async () => {
        try {
            const token = await getToken();
            if (!token) {
                throw new Error('認証トークンが取得できませんでした。');
            }

            // バックエンドにPUTリクエストを送信
            await axios.put(
                `${process.env.NEXT_PUBLIC_API_URL}/api/user/me/`,
                {
                    user_name: userName, // 更新するユーザー名
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            // ★★★ 成功したらセッションストレージにフラグを立てる ★★★
            sessionStorage.setItem('hanten_registration_complete', 'true');

            // 成功したらアプリ説明画面へ
            router.push('/tutorial/explain');
        } catch (error) {
            console.error('ユーザー情報の更新に失敗しました:', error);
            // ここでエラーメッセージをユーザーに表示する処理を追加するとより親切です
            alert('エラーが発生しました。もう一度お試しください。');
        }
    };

    const handleBack = () => {
        router.push(`/tutorial?username=${encodeURIComponent(userName || '')}`);
    };

    if (!userName) {
        return (
            <div className={styles.container}>
                <div className={styles.card}>
                    <p>ユーザー名が指定されていません。前のページに戻ってください。</p>
                    <button onClick={handleBack} className={styles.backButton}>戻る</button>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>登録確認</h1>
                <p className={styles.description}>ユーザー名</p>
                <p className={styles.usernameDisplay}>{userName}</p>

                <div className={styles.buttonContainer}>
                    <button onClick={handleBack} className={styles.backButton}>
                        戻る
                    </button>
                    <button onClick={handleRegister} className={styles.registerButton}>
                        登録
                    </button>
                </div>
            </div>
        </div>
    )
}

// Suspenseでラップして、searchParamsを安全に使用します
export default function page() {
    return (
        <Suspense fallback={<div>読み込み中...</div>}>
            <CheckComponent />
        </Suspense>
    );
}
