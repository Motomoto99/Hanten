'use client';

import styles from '../../css/Debates.module.css';

// APIから受け取るディベート部屋の型を定義
export interface Debate {
  id: number;
  room_name: string;
  room_start: string;
  room_end: string;
  theme_title: string;
}

interface Props {
  debate: Debate;
  onClick: () => void; // 親コンポーネントにクリックを通知
}

export default function Content({ debate, onClick }: Props) {
  const startDate = new Date(debate.room_start).toLocaleDateString();
  const endDate = new Date(debate.room_end).toLocaleDateString();

  return (
    <div className={styles.contentCard} onClick={onClick}>
      <div className={styles.dateRange}>{startDate} 〜 {endDate}</div>
      <h3 className={styles.roomName}>{debate.room_name}</h3>
      <div className={styles.participantInfo}>
        25人が参加中
      </div>
    </div>
  );
}