'use client';
import { Message } from '@/app/types/debate';
import styles from '../../css/Chat.module.css';

export default function OtherComment({ message }: { message: Message }) {
    return (
        <div className={`${styles.commentRow} ${styles.otherRow}`}>
            <div className={styles.avatar}>{message.sender.user_name.charAt(0)}</div>
            <div className={styles.commentContent}>
                <div className={styles.senderName}>{message.sender.user_name}</div>
                <div className={styles.otherCommentBubble}>
                    {message.content}
                </div>
            </div>
        </div>
    );
}