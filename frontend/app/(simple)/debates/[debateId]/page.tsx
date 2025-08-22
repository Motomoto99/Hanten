'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import axios from 'axios';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import DebateHeader from '@/app/components/chat/DebateHeader';
import CommentInput from '@/app/components/chat/CommentInput';
import { Message, DebateDetailData } from '@/app/types/debate';
import CommentList from '@/app/components/chat/CommentList';
import styles from '../../../css/Chat.module.css';
// import DebateFinishedPopup from '@/app/components/debates/DebateFinishedPopup';

export default function ChatPage() {
    const params = useParams<{ debateId: string }>(); // paramsは、URLのパラメータを取得するためのもの
    const debateId = params.debateId;
    const { user } = useUser(); // Clerkから現在のユーザー情報を取得
    const { getToken } = useAuth(); // Clerkからトークンを取得するためのフック

    const [messages, setMessages] = useState<Message[]>([]); // メッセージ一覧の状態を管理するためのuseStateフック
    const [socketUrl, setSocketUrl] = useState<string | null>(null);
    const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null); // ディベートの詳細情報を管理するためのuseStateフック
    const [isLoading, setIsLoading] = useState(true); // データの読み込み状態を管理するためのuseStateフック

    const [content, setContent] = useState(''); // コメント入力欄の内容を管理するためのuseStateフック
    const [showNewMessageIndicator, setShowNewMessageIndicator] = useState(false);
    const commentListRef = useRef<HTMLDivElement | null>(null);
    const router = useRouter(); // Next.jsのルーターを使用して、ページ遷移を行うためのフック

    
    //WebSocketのURLを生成するためのuseEffectフック
    useEffect(() => {
        // この関数は、初回の描画後と、debateIdかgetTokenが変わった時だけ実行される
        const generateUrl = async () => {
            // 本番用の認証に備え、Clerkのトークンも取得しておきます
            const token = await getToken();
            if (token) {
                // 今が本番(production)か、開発(development)かを判断
                const isProduction = process.env.NODE_ENV === 'production';

                const baseUrl = isProduction
                    ? process.env.NEXT_PUBLIC_WS_URL // 本番環境のURL
                    : 'ws://localhost:8000';         // 開発環境のURL

                const newSocketUrl = `${baseUrl}/ws/debates/${debateId}/`;

                // 3. 生成したURLを、「記憶ノート」に書き込み、Reactに「覚えておいて！」と伝えます
                setSocketUrl(newSocketUrl);
                console.log("WebSocket URLを生成しました:", newSocketUrl);
            }
        };
        generateUrl();
    }, [debateId, getToken]);
    // WebSocketの接続を管理するためのuseWebSocketフック
    const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl, {
        // socketUrlがnullの間は、接続を試みない
        shouldReconnect: (closeEvent) => true,
    });

    // 既読状態を更新するための関数
    const updateReadStatus = useCallback(async (lastCommentId: number) => {
        try {
            const token = await getToken();
            await axios.post(
                `${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/read_status/`,
                { last_read_comment_id: lastCommentId },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            console.log(`既読状態をコメントID:${lastCommentId}で更新しました。`);
        } catch (error) {
            console.error("既読の更新に失敗しました:", error);
        }
    }, [debateId, getToken]);

    // 初期データの取得を行うuseEffectフック
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

                    const lastReadId = messagesRes.data.last_read_comment_id;
                    console.log("最後に既読とされたコメントID:", lastReadId);

                    // ★★★ 取得したIDの要素までスクロール ★★★
                    setTimeout(() => { // DOMの描画を待つため
                        if (lastReadId) {
                            const element = document.getElementById(`comment-${lastReadId}`);
                            element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        } else {
                            // 既読がなければ一番下にスクロール
                            commentListRef.current?.scrollTo(0, commentListRef.current.scrollHeight);
                        }
                    }, 100);

                } else {
                    // もし期待と違うものが届いたら、エラーとして記録する
                    console.error("APIからのレスポンス形式が不正です。'results'配列が含まれていません。", messagesRes.data);
                    // 念のため、空の配列をセットして、画面がクラッシュするのを防ぐ
                    setMessages([]);
                }
            } catch (error) {
                console.error("初期データの取得に失敗:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchInitialData();
    }, [params.debateId]);

    // 新しいメッセージが届いたときの処理を行うuseEffectフック
    useEffect(() => {
        console.log("新しいメッセージが届きました:", lastMessage);
        if (lastMessage !== null) {
            const isScrolledToBottom = commentListRef.current && commentListRef.current.scrollHeight - commentListRef.current.scrollTop <= commentListRef.current.clientHeight + 100;
            console.log("スクロールのタカさ:", commentListRef.current?.scrollHeight);
            console.log("現在のスクロール位置:", commentListRef.current?.scrollTop);
            const data = JSON.parse(lastMessage.data);
            if (data.type === 'chat_message') {
                const newMessage: Message = data.message;
                setMessages((prevMessages) => [...prevMessages, newMessage]);
                if (newMessage.sender.clerk_user_id !== user?.id && !isScrolledToBottom) {
                    setShowNewMessageIndicator(true);
                } else {
                    // それ以外（自分が送ったか、一番下で見た）の場合は、自動でスクロールし、既読を更新
                    setTimeout(() => {
                        commentListRef.current?.scrollTo({ top: commentListRef.current.scrollHeight, behavior: 'smooth' });
                        updateReadStatus(newMessage.id); // ★★★ 既読を更新！ ★★★
                    }, 100);
                }
            }
            console.log("現在のメッセージ一覧:", messages);
        }
    }, [lastMessage]);


    // メッセージ送信処理
    const handleSendMessage = (content: string) => {
        if (user && readyState === ReadyState.OPEN) {
            const payload = {
                message: content,
                clerk_user_id: user.id
            };
            // ▼▼▼【useWebSocket.sendMessage を、ただの sendMessage に修正】▼▼▼
            sendMessage(JSON.stringify(payload));
        }
        console.log("メッセージ送信:", content);
        setContent(''); // メッセージ送信後は入力欄をクリア
    }

    // スクロールイベントを監視して、既読状態を更新するuseEffectフック
    const userScrolled = useRef(false);
    useEffect(() => {
        const listElement = commentListRef.current;
        console.log("コメントリストの要素:", listElement);
        if (!listElement) return;

        let timeoutId: NodeJS.Timeout;
        const handleScroll = () => {
            userScrolled.current = true;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                // 逆さまの世界では、「一番下」とは「scrollTopが0に近い」こと
                const isAtBottom = listElement.scrollTop > -20;
                console.log("現在のスクロール位置:", listElement.scrollTop);

                if (isAtBottom && messages.length > 0) {
                    updateReadStatus(messages[messages.length - 1].id);
                    // ★★★ 一番下まで来たら、新着通知はそっと消す ★★★
                    console.log("一番下までスクロールしました。新着通知を消します。");
                    if (showNewMessageIndicator) {
                        setShowNewMessageIndicator(false);
                    }
                }
            }, 500);

        };

        listElement.addEventListener('scroll', handleScroll);
        return () => listElement.removeEventListener('scroll', handleScroll);
    }, [messages]); // showNewMessageIndicatorも依存配列に追加

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
            <div className={styles.commentEreaWrapper}>
                <CommentList ref={commentListRef} messages={messages} />
            </div>

            {/* ★★★ 新着メッセージのお知らせボタン ★★★ */}
            {showNewMessageIndicator && (
                <button onClick={() => {
                    commentListRef.current?.scrollTo({ top: commentListRef.current.scrollHeight, behavior: 'smooth' });
                    setShowNewMessageIndicator(false);
                }} className={styles.newMessageButton}>
                    ↓ 新着メッセージ
                </button>
            )}

            <CommentInput
                value={content}
                onChange={setContent}
                onSendMessage={handleSendMessage}
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