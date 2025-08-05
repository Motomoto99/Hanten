'use client'

import React from 'react'

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';

// ユーザー情報の型を定義しておくと、コードが安全になります
interface UserProfile {
    id: number;
    clerk_user_id: string;
    user_name: string;
    first_flag: boolean;
}

export default function page() {
    const router = useRouter();
    const [loading, setLoading] = useState(true); // ローディング状態を管理
    const { getToken } = useAuth(); // getToken関数を取得

    useEffect(() => {
        // ユーザー情報をチェックする関数
        const checkUserStatus = async () => {
            try {
                // Clerkから認証トークン（会員証）を取得
                const token = await getToken();

                // バックエンドに自分の情報を問い合わせる
                const response = await axios.get<UserProfile>(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/`,
                    {
                        headers:{
                            Authorization: `Bearer ${token}`
                        }
                    }
                );
                const user = response.data;

                // もしfirst_flagがTrueだったら...
                if (user.first_flag) {
                    // チュートリアルページに強制的にリダイレクト！
                    router.push('/tutorial');
                } else {
                    // Falseなら、ローディングを終了してこのページを表示
                    setLoading(false);
                }
            } catch (error) {
                console.error("ユーザー情報の取得に失敗しました:", error);
                // エラーが起きた場合も、とりあえずページは表示させる
                setLoading(false);
            }
        };
        // このページが表示されたら、すぐにチェックを実行
        checkUserStatus();
    }, [router]); // useEffectの依存配列にrouterを追加

    // ローディング中は、何も表示しないか、ローディング画面を表示
    if (loading) {
        return <div>Now Loading...</div>;
    }

    return (
        <div>
            ディベート一覧を表示させます。

        </div>
    )
}
