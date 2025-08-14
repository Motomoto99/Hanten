'use client';
import  {Message}  from '@/app/types/debate';
import styles from '../../css/Chat.module.css';

export default function MyComment({ message }: { message: Message }) {
    return (
        <div className={`${styles.commentRow} ${styles.myRow}`}>
            <div className={styles.myCommentBubble}>
                {message.content}
            </div>
        </div>
    );
}