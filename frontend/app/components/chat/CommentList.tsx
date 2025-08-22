'use client';
import React, { forwardRef } from 'react';
import { Message } from '@/app/types/debate';
import MyComment from './MyComment';
import OtherComment from './OtherComment';
import { useUser } from '@clerk/nextjs';
import styles from '../../css/Chat.module.css';

interface Props {
    messages: Message[];
}

const CommentList = forwardRef<HTMLDivElement, Props>(
    ({ messages }, ref) => {
        const { user } = useUser();
        const reversedMessages = [...messages].reverse();
        return (
            <div ref={ref} className={styles.commentList}>
                {reversedMessages.map(msg =>
                    user?.id === msg.sender.clerk_user_id
                        ? <MyComment key={msg.id} message={msg} />
                        : <OtherComment key={msg.id} message={msg} />
                )}
            </div>
        );
    }
)

export default CommentList;