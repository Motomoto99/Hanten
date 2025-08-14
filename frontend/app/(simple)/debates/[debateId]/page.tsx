'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import axios from 'axios';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import DebateHeader from '@/app/components/chat/DebateHeader';
import CommentInput from '@/app/components/chat/CommentInput';
import { Message, DebateDetailData } from '@/app/types/debate';
import CommentList from '@/app/components/chat/CommentList';
import styles from '../../../css/Chat.module.css';
// import MessageInput from '@/app/components/debates/MessageInput';
// import DebateFinishedPopup from '@/app/components/debates/DebateFinishedPopup';


export default function ChatPage() {
    const params = useParams<{ debateId: string }>();
    const debateId = params.debateId;
    const { user } = useUser();
    const { getToken } = useAuth();

    const [messages, setMessages] = useState<Message[]>([]);
    const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [content, setContent] = useState('');

    const [lastReadTimestamp, setLastReadTimestamp] = useState<string | null>(null);

    // 初回マウント時に、部屋情報（終了日時を含む）と過去のメッセージを取得
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const token = await getToken();
                // 部屋の詳細情報を取得
                const detailRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${params.debateId}/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setDebateDetail(detailRes.data);

                // 過去のメッセージを取得
                const messagesRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${params.debateId}/messages/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });

                // 監視カメラを設置：届いた荷物の中身を、まず目で見る！
                console.log("バックエンドから届いた生データ:", messagesRes.data);

                // 荷物の中身が、本当に期待通りの形をしているか、厳しくチェックする
                if (messagesRes.data && Array.isArray(messagesRes.data.results)) {
                    // 安全が確認できたので、部品（messages）をセットする
                    setMessages(messagesRes.data.results);

                } else {
                    // もし期待と違うものが届いたら、エラーとして記録する
                    console.error("APIからのレスポンス形式が不正です。'results'配列が含まれていません。", messagesRes.data);
                    // 念のため、空の配列をセットして、画面がクラッシュするのを防ぐ
                    setMessages([]);
                }


                // // ★★★ 既読状態を「今」に更新するAPIを叩く ★★★
                // await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/read_status/`, {}, {
                //     headers: { Authorization: `Bearer ${token}` }
                // });

            } catch (error) {
                console.error("初期データの取得に失敗:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchInitialData();
    }, [params.debateId, getToken]);


    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `ws://localhost:8000/ws/debates/${debateId}/`;
    const { sendMessage, lastMessage, readyState } = useWebSocket(wsUrl, {
        shouldReconnect: (closeEvent) => true, // 常に再接続を試みる
    });
    // サーバーから新しいメッセージが届くたびに、このuseEffectが実行される
    useEffect(() => {
        if (lastMessage !== null) {
            const data = JSON.parse(lastMessage.data);
            if (data.type === 'chat_message') {
                setMessages((prevMessages) => [...prevMessages, data.message]);
            }
        }
    }, [lastMessage, setMessages]);



    const handleSendMessage = (content: string) => {
        if (user && readyState === ReadyState.OPEN) {
            const payload = {
                message: content,
                clerk_user_id: user.id
            };
            // ▼▼▼【useWebSocket.sendMessage を、ただの sendMessage に修正】▼▼▼
            sendMessage(JSON.stringify(payload));
        }
    }

    // 接続状態を文字列で表示（デバッグ用）
    const connectionStatus = {
        [ReadyState.CONNECTING]: '接続中...',
        [ReadyState.OPEN]: '接続完了',
        [ReadyState.CLOSING]: '切断中...',
        [ReadyState.CLOSED]: '切断',
        [ReadyState.UNINSTANTIATED]: '未準備',
    }[readyState];


    // ★★★ 終了判定ロジック ★★★
    const isDebateFinished = debateDetail && new Date(debateDetail.room_end) < new Date();

    if (isLoading) {
        return <div>ディベート部屋を準備中...</div>;
    }

    if (isDebateFinished) {
        return (
            <div>
                {/* ★★★ 終了表示ポップアップコンポーネント ★★★ */}
                {/* <DebateFinishedPopup debateDetail={debateDetail} /> */}
                <h1>このディベートは終了しました</h1>
            </div>
        );
    }

    return (
        <div className={styles.chatContainer}>
            <DebateHeader debateId={debateId} side={debateDetail?.user_participation.position ?? null} />
            <div className='commentEreaWrapper'>
                <CommentList messages={messages} />
            </div>
            <CommentInput
                value={content}
                onChange={setContent}
                onSendMessage={sendMessage}
                isLoading={isLoading}
                placeholder={`${debateDetail?.user_participation.position === 'AGREE' ? '賛成' : '反対'}意見をここに入力...`}
            />

            {isDebateFinished && (
                <div className={styles.finishedOverlay}>
                    {/* ... (終了ポップアップ) ... */}
                </div>
            )}
        </div>

    );
}