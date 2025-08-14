'use client';
import { Message } from '@/app/types/debate';
import MyComment from './MyComment';
import OtherComment from './OtherComment';
import { useUser } from '@clerk/nextjs';
import styles from '../../css/Chat.module.css';

export default function CommentList({ messages }: { messages: Message[] }) {
    const { user } = useUser();
    return (
        <div className='guideBox'>
            {messages.map(msg =>
                user?.id === msg.sender.clerk_user_id
                    ? <MyComment key={msg.id} message={msg} />
                    : <OtherComment key={msg.id} message={msg} />
            )}
        </div>
    );
}