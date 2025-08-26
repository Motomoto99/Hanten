'use client'

import React from 'react'
import { useEffect, useState, useRef, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import { useAuth, useUser } from '@clerk/nextjs';
import ContentList from '@/app/components/content/ContentList';
import ContentDetail from '@/app/components/content/ContentDetail';
import { DebateDetailData } from '@/app/types/debate';
import { Debate } from '@/app/components/content/Content';
import { UserProfile } from '@/app/types/user'; // ユーザー情報の型をインポート
import styles from '@/app/css/Debates.module.css';

type Tab = 'ongoing' | 'finished';

function DebatesHistoryComopnent() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { isLoaded, isSignedIn } = useUser();

  //状態管理（State）を整理・統合
  const [pageLoading, setPageLoading] = useState(true); // ページ全体のローディング状態を管理
  const [activeTab, setActiveTab] = useState<Tab>('ongoing');
  const [debates, setDebates] = useState<{ [key in Tab]: Debate[] }>({ ongoing: [], finished: [] });
  const [tabLoading, setTabLoading] = useState(false); // タブごとのデータ読み込み
  // データを取得したタブを記録
  const [fetchedTabs, setFetchedTabs] = useState<Set<Tab>>(new Set());

  // モーダル関連のState
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedDebateId, setSelectedDebateId] = useState<number | null>(null);
  const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);


  // --- APIからデータを取得する関数（useCallbackで最適化）---
  const fetchDebates = useCallback(async (tab: Tab) => {
    // 既に読み込み中、または次のページがない場合は何もしない
    setTabLoading(true);
    try {
      const token = await getToken();
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/participate_debates/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { status: tab },
      });
      setDebates(prev => ({
        ...prev,
        [tab]: response.data
      }));
      setFetchedTabs(prev => new Set(prev).add(tab));
      console.log(`${tab}ディベートの取得に成功:`, response.data);
    } catch (error) {
      console.error(`${tab}ディベートの取得に失敗:`, error);
    } finally {
      setTabLoading(false);
    }
  }, [getToken]);


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
          if (!fetchedTabs.has('ongoing')) {
            await fetchDebates('ongoing');
          }
          setPageLoading(false);
        }
      } catch (error) {
        console.error("ユーザー情報の取得に失敗しました:", error);
        // エラー時はトップページなどに戻す
        router.push('/');
      }
    };

    checkUserStatus();
  }, [isLoaded, isSignedIn, getToken, router, fetchDebates, fetchedTabs]);

  // 2. タブが切り替わった時に、データが空ならデータを取得
  useEffect(() => {
    if (!pageLoading && !fetchedTabs.has(activeTab)) {
      fetchDebates(activeTab);
    }
  }, [activeTab, pageLoading, fetchDebates, fetchedTabs]);

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
    return <div className={styles.center}>読み込み中...</div>;
  }

  return (
    <div>
      <div className={styles.tabContainer}>
        <button
          className={activeTab === 'ongoing' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('ongoing')}
        >
          参加中
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
      />
      {tabLoading && <div className={styles.center}>読み込み中...</div>}
      {!tabLoading && debates[activeTab].length > 0 && (
        <div className={styles.center}>最後のディベートです</div>
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

export default function DebateHistoryPage() {
  return (
    <Suspense fallback={<div className={styles.center}>ページを準備中...</div>}>
      <DebatesHistoryComopnent />
    </Suspense>
  );
}