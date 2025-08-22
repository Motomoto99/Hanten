'use client';
import { Message } from '@/app/types/debate';
import styles from '../../css/Chat.module.css';

export default function MyComment({ message }: { message: Message }) {
    return (
        <div id={`comment-${message.id}`} className={`${styles.commentRow} ${styles.myRow}`}>
            <div className={styles.commentContent}>
                <div className={styles.senderInfo}>
                    {/* ★★★ 立場を表示するタグを追加 ★★★ */}
                    {message.position && (
                        <span className={`${styles.positionTagMy} ${message.position === '賛成' ? styles.agree : styles.disagree}`}>
                            {message.position}派
                        </span>
                    )}
                </div>
                <div className={styles.myCommentBubble}>
                    {message.comment_text}
                </div>
            </div>

        </div>
    );
}