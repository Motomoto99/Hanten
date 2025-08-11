'use client'

import React from 'react'
import { useEffect, useState, useRef, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import { useAuth, useUser } from '@clerk/nextjs';
import ContentList from '@/app/components/content/ContentList';
import ContentDetail, { DebateDetailData } from '@/app/components/content/ContentDetail';
import { Debate } from '@/app/components/content/Content';
import styles from '@/app/css/Debates.module.css';

type Tab = 'ongoing' | 'finished';

// ユーザー情報の型を定義しておくと、コードが安全になります
interface UserProfile {
    id: number;
    clerk_user_id: string;
    user_name: string;
    first_flag: boolean;
}

function DebatesComponent() {
    const router = useRouter();
    const { getToken } = useAuth();
    const { isLoaded, isSignedIn } = useUser();
    const searchParams = useSearchParams();

    //状態管理（State）を整理・統合
    const [pageLoading, setPageLoading] = useState(true); // ページ全体のローディング状態を管理
    const [activeTab, setActiveTab] = useState<Tab>('ongoing');
    const [debates, setDebates] = useState<{ [key in Tab]: Debate[] }>({ ongoing: [], finished: [] });
    const [nextPage, setNextPage] = useState<{ [key in Tab]: number | null }>({ ongoing: 1, finished: 1 });
    const [tabLoading, setTabLoading] = useState(false); // タブごとのデータ読み込み

    // モーダル関連のState
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedDebateId, setSelectedDebateId] = useState<number | null>(null);
    const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
    const [isDetailLoading, setIsDetailLoading] = useState(false);


    // --- APIからデータを取得する関数（useCallbackで最適化）---
    const fetchDebates = useCallback(async (tab: Tab, page: number) => {
        // 既に読み込み中、または次のページがない場合は何もしない
        if (tabLoading || !nextPage[tab]) return;

        setTabLoading(true);
        try {
            const token = await getToken();
            const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/`, {
                headers: { Authorization: `Bearer ${token}` },
                params: { status: tab, page: page },
            });
            setDebates(prev => ({
                ...prev,
                [tab]: page === 1 ? response.data.results : [...prev[tab], ...response.data.results],
            }));
            setNextPage(prev => ({
                ...prev,
                [tab]: response.data.next ? page + 1 : null,
            }));
        } catch (error) {
            console.error(`${tab}ディベートの取得に失敗:`, error);
        } finally {
            setTabLoading(false);
        }
    }, [getToken, tabLoading, nextPage]);

    // --- 無限スクロール ---
    const observer = useRef<IntersectionObserver | null>(null);
    const lastDebateElementRef = useCallback((node: HTMLDivElement | null) => {
        if (tabLoading) return;
        if (observer.current) observer.current.disconnect();
        
        observer.current = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && nextPage[activeTab] !== null) {
                fetchDebates(activeTab, nextPage[activeTab] as number);
            }
        });

        if (node) observer.current.observe(node);
    }, [tabLoading, activeTab, nextPage, fetchDebates]);


    // useEffectの処理

    // 1. 初回マウント時にユーザー状態をチェックし、チュートリアルへのリダイレクトを判断
    useEffect(() => {
        if (!isLoaded) return; // Clerkの準備ができるまで待つ

        if (!isSignedIn) {
            router.push('/sign-in');
            return;
        }

        const checkUserStatus = async () => {
            try {
                const token = await getToken();
                const response = await axios.get<UserProfile>(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                
                if (response.data.first_flag) {
                    router.push('/tutorial');
                } else {
                    // チュートリアルが不要なら、最初のデータを取得開始
                    fetchDebates('ongoing', 1);
                    setPageLoading(false);
                }
            } catch (error) {
                console.error("ユーザー情報の取得に失敗しました:", error);
                // エラー時はトップページなどに戻す
                router.push('/');
            }
        };

        checkUserStatus();
    }, [isLoaded, isSignedIn, getToken, router]);

    // 2. タブが切り替わった時に、データが空ならデータを取得
    useEffect(() => {
        if (!pageLoading && debates[activeTab].length === 0) {
            fetchDebates(activeTab, 1);
        }
    }, [activeTab, pageLoading, debates, fetchDebates]);

    // 3. 部屋作成後など、クエリパラメータで指定された場合にモーダルを開く
    useEffect(() => {
        const openDebateId = searchParams.get('open');
        if (openDebateId) {
            handleDebateClick(parseInt(openDebateId));
            router.replace('/debates', { scroll: false });
        }
    }, [searchParams, router]);
    
    // 4. 個別ディベートの詳細を取得
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

    if (pageLoading || !isLoaded) {
        return <div>読み込み中...</div>;
    }

    return (
        <div>
            <div className={styles.tabContainer}>
                <button
                    className={activeTab === 'ongoing' ? styles.activeTab : styles.tab}
                    onClick={() => setActiveTab('ongoing')}
                >
                    開催中
                </button>
                <button
                    className={activeTab === 'finished' ? styles.activeTab : styles.tab}
                    onClick={() => setActiveTab('finished')}
                >
                    終了済み
                </button>
            </div>

            <ContentList
                debates={debates[activeTab]}
                onDebateClick={handleDebateClick}
                ref={lastDebateElementRef}
            />
            {tabLoading && <div>読み込み中...</div>}
            {!tabLoading && !nextPage[activeTab] && debates[activeTab].length > 0 && (
                <div className={styles.endOfList}>最後のディベートです</div>
            )}

            {isModalOpen && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        <ContentDetail debateDetail={debateDetail} isLoading={isDetailLoading} />
                    </div>
                </div>
            )}
        </div>
    );
}

export default function DebatesPage() {
    return (
        <Suspense fallback={<div>ページを準備中...</div>}>
            <DebatesComponent />
        </Suspense>
    );
}