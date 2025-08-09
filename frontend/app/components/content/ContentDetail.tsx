'use client';

import { useRouter } from 'next/navigation';
import styles from '../../css/Debates.module.css';

// 詳細APIから受け取る型
export interface DebateDetailData {
  id: number;
  room_name: string;
  room_start: string;
  room_end: string;
  theme: {
    id: number;
    theme_title: string;
    theme_detail: string;
  };
  // 他にもcreator情報など
}

interface Props {
  debateDetail: DebateDetailData | null;
  isLoading: boolean;
}

export default function ContentDetail({ debateDetail, isLoading }: Props) {
  const router = useRouter();
  
  // TODO: ユーザーの参加状況を取得するAPIを後で作成する
  const isParticipating = false; // 仮のフラグ

  if (isLoading) {
    return <div>読み込み中...</div>;
  }
  if (!debateDetail) {
    return <div>詳細の取得に失敗しました。</div>;
  }

  const handleAgree = () => {
    router.push(`/debates/${debateDetail.id}/firstAdd?side=agree`);
  };

  const handleDisagree = () => {
    router.push(`/debates/${debateDetail.id}/firstAdd?side=disagree`);
  };

  const handleEnterRoom = () => {
    router.push(`/debates/${debateDetail.id}`);
  };

  return (
    <div className={styles.detailContainer}>
      <div className={styles.dateRange}>
        {new Date(debateDetail.room_start).toLocaleDateString()} 〜 {new Date(debateDetail.room_end).toLocaleDateString()}
      </div>
      <h2 className={styles.roomNameDetail}>{debateDetail.room_name}</h2>
      <h1 className={styles.themeTitle}>{debateDetail.theme.theme_title}</h1>
      <p className={styles.themeDetail}>{debateDetail.theme.theme_detail}</p>
      
      <div className={styles.buttonArea}>
        {isParticipating ? (
          <button onClick={handleEnterRoom} className={`${styles.btn} ${styles.btnEnter}`}>
            入室
          </button>
        ) : (
          <>
            <button onClick={handleAgree} className={`${styles.btn} ${styles.btnAgree}`}>
              賛成
            </button>
            <button onClick={handleDisagree} className={`${styles.btn} ${styles.btnDisagree}`}>
              反対
            </button>
          </>
        )}
      </div>
    </div>
  );
}