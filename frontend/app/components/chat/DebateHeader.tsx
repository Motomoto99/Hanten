'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';
import styles from '../../css/Debates.module.css';
import { DebateDetailData } from '@/app/types/debate';
import stylesSide from '@/app/css/FirstAdd.module.css';

interface Props {
  debateId: string; // ディベートのID
  side: string | null; // ユーザーの立場（賛成・反対）
}

export default function DebateHeader({ debateId, side }: Props) {
  const router = useRouter();
  const { getToken } = useAuth();

  // ★★★ このコンポーネント自身が、データとローディング状態を管理する ★★★
  const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);


  // ★★★ debateIdが変わるたびに、APIから詳細データを取得する ★★★
  useEffect(() => {
    if (debateId) {
      const fetchDebateDetail = async () => {
        setIsLoading(true);
        try {
          const token = await getToken();
          const response = await axios.get(
            `${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          setDebateDetail(response.data);
        } catch (error) {
          console.error("ヘッダー用のディベート詳細取得に失敗:", error);
          setDebateDetail(null);
        } finally {
          setIsLoading(false);
        }
      };
      fetchDebateDetail();
    }
  }, [debateId, getToken]);


  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  // ローディング中やデータがない場合は、シンプルな表示
  if (isLoading || !debateDetail) {
    return (
      <header className={styles.debateHeader}>
        <button onClick={() => router.back()} className={styles.backButton}>
          &lt;
        </button>
        <div className={styles.headerTitle}>読み込み中...</div>
      </header>
    );
  }

  const oppositeSide = side === 'agree' ? '反対' : '賛成';
  const oppositeSideClass = side === 'agree' ? stylesSide.disagree : stylesSide.agree;

  return (
    <>
      <header className={styles.debateHeader}>
        <button onClick={() => router.back()} className={styles.backButton}>
          &lt;
        </button>
        <div className={styles.headerTitleClickable} onClick={openModal}>
          <h1 className={styles.headerTitle}>{debateDetail.room_name}</h1>
        </div>
      </header>

      {/* ポップアップ（モーダル）表示 */}
      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.detailContainer}>
              <div className={styles.dateRange}>
                {new Date(debateDetail.room_start).toLocaleDateString()} 〜 {new Date(debateDetail.room_end).toLocaleDateString()}
              </div>
              <h2 className={styles.roomNameDetail}>{debateDetail.room_name}</h2>
              <h1 className={styles.themeTitle}>{debateDetail.theme.theme_title}</h1>
              <p className={styles.themeDetail}>{debateDetail.theme.theme_detail}</p>

              <div className={styles.buttonArea}>
                <div>
                  あなたは<span className={oppositeSideClass}>{oppositeSide}派</span>として<br />
                  この議論に参加しています
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}