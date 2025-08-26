'use client';

import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import styles from '../../css/Debates.module.css';
import { DebateDetailData } from '@/app/types/debate';



interface Props {
  debateDetail: DebateDetailData | null;
  isLoading: boolean;
}

export default function ContentDetail({ debateDetail, isLoading }: Props) {
  const router = useRouter();
  const { user } = useUser();

  const userId = user?.id;


  if (isLoading) {
    return <div>読み込み中...</div>;
  }
  if (!debateDetail) {
    return <div>詳細の取得に失敗しました。</div>;
  }

  const isDebateFinished = new Date(debateDetail.room_end) < new Date();

  const handleAgree = () => {
    router.push(`/debates/${debateDetail.id}/firstAdd?side=agree`);
  };

  const handleDisagree = () => {
    router.push(`/debates/${debateDetail.id}/firstAdd?side=disagree`);
  };

  const handleEnterRoom = () => {
    router.push(`/debates/${debateDetail.id}`);
  };
  const handleCheckEvaluation = () => {
    router.push(`/users/${userId}/history/${debateDetail.id}`);
  }

  return (
    <div className={styles.detailContainer}>
      <div className={styles.dateRange}>
        {new Date(debateDetail.room_start).toLocaleDateString()} 〜 {new Date(debateDetail.room_end).toLocaleDateString()}
      </div>
      <h2 className={styles.roomNameDetail}>{debateDetail.room_name}</h2>
      <h1 className={styles.themeTitle}>{debateDetail.theme.theme_title}</h1>
      <p className={styles.themeDetail}>{debateDetail.theme.theme_detail}</p>

      <div className={styles.buttonArea}>
        {isDebateFinished ? (
          // --- 終了後のボタン ---
          debateDetail.is_participating ? (
            // 参加済みの場合
            <button onClick={handleCheckEvaluation} className={`${styles.btn} ${styles.btnConfirm}`}>
              評価確認
            </button>
          ) : (
            // 未参加の場合 何もボタンを置かない
            <p>すでに終了しています</p>
          )
        ) : (
          // --- 開催中のボタン ---
          debateDetail.is_participating ? (
            // 参加済みの場合
            <button onClick={handleEnterRoom} className={`${styles.btn} ${styles.btnEnter}`}>
              入室
            </button>
          ) : (
            // 未参加の場合
            <>
              <button onClick={handleAgree} className={`${styles.btn} ${styles.btnAgree}`}>
                賛成
              </button>
              <button onClick={handleDisagree} className={`${styles.btn} ${styles.btnDisagree}`}>
                反対
              </button>
            </>
          )
        )}
      </div>
    </div>
  );
}