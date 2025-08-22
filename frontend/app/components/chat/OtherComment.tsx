'use client';
import { Message } from '@/app/types/debate';
import styles from '../../css/Chat.module.css';

export default function OtherComment({ message }: { message: Message }) {
    return (
        <div id={`comment-${message.id}`} className={`${styles.commentRow} ${styles.otherRow}`}>
            <div className={styles.commentContent}>
                <div className={styles.senderInfo}>
                    <span className={styles.senderName}>{message.sender.user_name}</span>
                    {/* ★★★ 立場を表示するタグを追加 ★★★ */}
                    {message.position && (
                        <span className={`${styles.positionTagOther} ${message.position === '賛成' ? styles.agree : styles.disagree}`}>
                            {message.position}派
                        </span>
                    )}
                </div>
                <div className={styles.otherCommentBubble}>
                    {message.comment_text}
                </div>
            </div>
        </div>
    );
}