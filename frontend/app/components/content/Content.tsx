'use client';

import styles from '../../css/Debates.module.css';
import { Debate } from '@/app/types/debate';

interface Props {
  debate: Debate;
  onClick: () => void; // 親コンポーネントにクリックを通知
}

export default function Content({ debate, onClick }: Props) {
  const startDate = new Date(debate.room_start).toLocaleString('ja-JP');
  const endDate = new Date(debate.room_end).toLocaleString('ja-JP');
  const isFinished = new Date(debate.room_end) <= new Date();

  return (
    <div className={styles.contentCard} onClick={onClick}>
      <div className={styles.date}>
        <div className={styles.dateRange}>{startDate} 〜 {endDate}</div>
        {debate.has_unread_messages && debate.is_participating && (
          <div className={styles.unreadIndicator}>新着コメントあり</div>
        )}
      </div>
      <h3 className={styles.roomName}>{debate.room_name}</h3>
      <div className={styles.participantInfo}>
        <span className={styles.count}>
          {debate.participant_count}人
        </span>
        <span className={styles.participant}>
          {isFinished ? 'が参加しました' : 'が参加中'}
        </span>
      </div>
    </div>
  );
}