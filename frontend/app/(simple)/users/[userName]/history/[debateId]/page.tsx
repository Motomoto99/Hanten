'use client'

import React from 'react'

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth, useUser } from '@clerk/nextjs';
import axios from 'axios';
import DebateHeader from '@/app/components/chat/DebateHeader';
import { DebateDetailData } from '@/app/types/debate';
import CommentList from '@/app/components/chat/CommentList';
import { Message } from '@/app/types/debate';
import styles from '@/app/css/Feedback.module.css';

// APIから受け取る成績表の型
interface EvaluationData {
    my_comment_count: number;
    my_comment_percentage: number;
    total_comment_count: number;
    agree_percentage: number;
    disagree_percentage: number;
}


export default function EvaluationPage() {
    const params = useParams<{ userName: string, debateId: string }>();
    const debateId = params.debateId;
    const router = useRouter();
    const { getToken } = useAuth();
    const { user } = useUser();

    const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
    const [feedback, setFeedback] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isAILoading, setIsAILoading] = useState(false);
    const [evaluation, setEvaluation] = useState<EvaluationData | null>(null);
    const [hasFeedback, setHasFeedback] = useState(false);

    const [showChat, setShowChat] = useState(false);
    const [chatMessages, setChatMessages] = useState<Message[]>([]);
    const [isChatLoading, setIsChatLoading] = useState(false);

    const userId = user?.id;

    useEffect(() => {
        const fetchDebate = async () => {
            try {
                const token = await getToken();

                const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setDebateDetail(res.data);

                const feedbackRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/feedback/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (feedbackRes.data.feedback) {
                    setFeedback(feedbackRes.data.feedback);
                    setHasFeedback(true); // 取得できたら、フラグを立てる
                }


                const evaluationRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/${debateId}/evaluation/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setEvaluation(evaluationRes.data);

                // もしディベートが終了していなければ、履歴ページに戻す
                if (new Date(res.data.room_end) >= new Date()) {
                    router.replace(`/users/${userId}/history`);
                    return;
                }
            } catch (error) {
                console.error("データ（ディベート詳細、フィードバック、成績）の取得に失敗", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchDebate();
    }, [debateId]);

    const handleGenerateFeedback = async () => {
        setIsAILoading(true);
        try {
            const token = await getToken();
            const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/feedback/`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setFeedback(res.data.feedback);
        } catch (error) {
            console.error("AIフィードバックの生成に失敗", error);
            setFeedback("エラーが発生しました。");
        } finally {
            setIsAILoading(false);
        }
    };

    // ★★★ トグルが押された時に、チャット履歴を取得する関数 ★★★
    const handleFetchChat = async () => {
        // もし、もうチャットを開いているなら、何もしない
        if (showChat) {
            setShowChat(false); // トグルなので、もう一度押したら閉じます
            return;
        }

        setIsChatLoading(true);
        if(chatMessages){
            setShowChat(true); // 既に取得済みなら、すぐに表示
            setIsChatLoading(false);
            return;
        }
        try {
            const token = await getToken();
            const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/messages/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setChatMessages(res.data.results);
            setShowChat(true); // データを取得できたら、表示を許可
        } catch (error) {
            console.error("チャット履歴の取得に失敗", error);
        } finally {
            setIsChatLoading(false);
        }
    };

    if (isLoading) return <div>読み込み中...</div>;

    const positionStyle = debateDetail?.user_participation.position === 'AGREE' ? styles.agree : styles.disagree;
    const talkPositionStyle = debateDetail?.user_participation.position === 'AGREE' ? styles.disagree : styles.agree;

    return (
        <div>
            <DebateHeader debateId={debateId} side={debateDetail?.user_participation.position ?? null} />
            <div className={styles.container}>
                <h1 className={styles.title}>ディベート評価</h1>
                <div className={styles.envaluationTop}>
                    <p>最初に選択した立場 :　<span className={talkPositionStyle}>{debateDetail?.user_participation?.position == 'AGREE' ? "反対" : "賛成"}</span></p>
                    <p>議論での立場 :　<span className={positionStyle}>{debateDetail?.user_participation?.position == 'AGREE' ? "賛成" : "反対"}</span></p>
                </div>

                <div className={styles.card}>
                    <h2>議論の比率（議論での立場）</h2>
                    <div className={styles.ratioBar}>
                        <div className={styles.agreeBar} style={{ width: `${evaluation?.agree_percentage}%` }}>
                            賛成 {evaluation?.agree_percentage}%
                        </div>
                        <div className={styles.disagreeBar} style={{ width: `${evaluation?.disagree_percentage}%` }}>
                            反対 {evaluation?.disagree_percentage}%
                        </div>
                    </div>
                </div>

                {/* あなたの貢献度 */}
                <div className={styles.card}>
                    <h2>あなたの貢献度</h2>
                    <div className={styles.metrics}>
                        <div className={styles.metricItem}>
                            <div className={styles.metricValue}>{evaluation?.my_comment_count}</div>
                            <div className={styles.metricLabel}>コメント数</div>
                        </div>
                        <div className={styles.metricItem}>
                            {/* ★★★ これが、私からのおすすめグラフです！ ★★★ */}
                            <div className={styles.metricValue}>{evaluation?.my_comment_percentage}<span>%</span></div>
                            <div className={styles.metricLabel}>コメントシェア率</div>
                        </div>
                    </div>
                    <p className={styles.summaryText}>
                        この議論は合計<span className={styles.strong}>{evaluation?.total_comment_count}</span>件のコメントで構成され、
                        あなたはそのうちの <strong><span className={styles.strong}>{evaluation?.my_comment_percentage}</span>%</strong> を担いました。
                    </p>
                </div>

                <hr />
                <br></br>


                {hasFeedback ? (
                    <div className={styles.card}>
                        <h2>AIからのフィードバック</h2>
                        <p style={{ whiteSpace: 'pre-wrap' }}>{feedback}</p>
                    </div>
                ) : (
                    <div className={styles.actionButtons}>
                        <button className={styles.aiButton} onClick={handleGenerateFeedback} disabled={isAILoading}>
                            {isAILoading ? 'AIが分析中...' : 'AIフィードバックを生成する'}
                        </button>
                    </div>
                )}

                <div className={styles.card}>
                    <button onClick={handleFetchChat} className={styles.toggleButton}>
                        {showChat ? '議論を隠す' : '議論の内容を見る'}
                    </button>
                    {isChatLoading && <div>読み込み中...</div>}
                    {showChat && (
                        <div className={styles.chatHistoryContainer}>
                            <CommentList messages={chatMessages}  />
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}