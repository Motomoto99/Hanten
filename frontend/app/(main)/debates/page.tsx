'use client'

import React from 'react'

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useAuth, useUser } from '@clerk/nextjs';
import ContentList from '@/app/components/content/ContentList';
import ContentDetail, { DebateDetailData } from '@/app/components/content/ContentDetail';
import { Debate } from '@/app/components/content/Content';
import styles from '@/app/css/Debates.module.css';

// ユーザー情報の型を定義しておくと、コードが安全になります
interface UserProfile {
    id: number;
    clerk_user_id: string;
    user_name: string;
    first_flag: boolean;
}

export default function page() {
    const router = useRouter();
    const [ongoingDebates, setOngoingDebates] = useState<Debate[]>([]);
    const [finishedDebates, setFinishedDebates] = useState<Debate[]>([]);
    const [loading, setLoading] = useState(true); // ローディング状態を管理
    const { getToken } = useAuth();
    const { isLoaded, isSignedIn, user } = useUser();

    // --- ポップアップ（モーダル）関連のState ---
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedDebateId, setSelectedDebateId] = useState<number | null>(null);
    const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
    const [isDetailLoading, setIsDetailLoading] = useState(false);

    useEffect(() => {
        // ユーザー情報をチェックする関数
        if (isLoaded && isSignedIn) {
            const checkUserStatus = async () => {
                try {
                    // Clerkから認証トークン（会員証）を取得
                    const token = await getToken();

                    // console.log("取得したトークン:", token);

                    if (!token) {
                        console.error("トークンが取得できませんでした。リクエストを中断します。");
                        setLoading(false);
                        return; // トークンがなければ、APIを呼び出さない！
                    }

                    // バックエンドに自分の情報を問い合わせる
                    const response = await axios.get<UserProfile>(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/`,
                        {
                            headers: {
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
                    router.push('/'); // デフォルトのページにリダイレクト
                }
            };
            // このページが表示されたら、すぐにチェックを実行
            checkUserStatus();
        }
        // もしClerkの準備ができたのに、サインインしていなかったらログインページに飛ばす
        if (isLoaded && !isSignedIn) {
            router.push('/sign-in');
        }
    }, [isLoaded, isSignedIn, router, getToken]); // useEffectの依存配列にrouterを追加

    // ディベート一覧を取得
    useEffect(() => {
        const fetchDebates = async () => {
            try {
                const token = await getToken();
                const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/`, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                const now = new Date();
                const ongoing = response.data.filter((d: Debate) => new Date(d.room_end) > now);
                const finished = response.data.filter((d: Debate) => new Date(d.room_end) <= now);

                setOngoingDebates(ongoing);
                setFinishedDebates(finished);
            } catch (error) {
                console.error("ディベート一覧の取得に失敗しました:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchDebates();
    }, [getToken]);

    // ディベート詳細を取得
    useEffect(() => {
        if (selectedDebateId !== null) {
            const fetchDebateDetail = async () => {
                setIsDetailLoading(true);
                try {
                    const token = await getToken();
                    const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${selectedDebateId}/`, {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    setDebateDetail(response.data);
                } catch (error) {
                    console.error("ディベート詳細の取得に失敗しました:", error);
                    setDebateDetail(null);
                } finally {
                    setIsDetailLoading(false);
                }
            };
            fetchDebateDetail();
        }
    }, [selectedDebateId, getToken]);

    const handleDebateClick = (debateId: number) => {
        setSelectedDebateId(debateId);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedDebateId(null);
        setDebateDetail(null);
    };

    if (loading) {
        return <div>読み込み中...</div>;
    }


    // ローディング中は、何も表示しないか、ローディング画面を表示
    if (!isLoaded) {
        return <div>セッション情報を確認中...</div>;
    }


    return (
        <div>
            <ContentList
                title="開催中のディベート部屋"
                debates={ongoingDebates}
                onDebateClick={handleDebateClick}
            />
            <ContentList
                title="終了したディベート部屋"
                debates={finishedDebates}
                onDebateClick={handleDebateClick}
            />

            {/* ポップアップ（モーダル）表示 */}
            {isModalOpen && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        <ContentDetail debateDetail={debateDetail} isLoading={isDetailLoading} />
                    </div>
                </div>
            )}
        </div>
    )
}
