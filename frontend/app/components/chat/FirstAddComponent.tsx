'use client';

import { useState } from 'react';
import { useRouter, useSearchParams, useParams } from 'next/navigation';
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';
import styles from '../../css/FirstAdd.module.css';
import CommentInput from '@/app/components/chat/CommentInput';
import DebateHeader from '@/app/components/chat/DebateHeader';

export default function FirstAddComponent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const params = useParams<{ debateId: string }>();
  const debateId = params.debateId;

  const side = searchParams.get('side');
  const { getToken } = useAuth();

  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);


  // const handlePostFirstMessage = (message: string) => {
  //   setContent(message);
  //   setShowConfirmModal(true);
  // };

  const handleShowConfirmModal = () => {
    if(content.trim()){
      setShowConfirmModal(true);
    }
  };

  const handleSubmit = async () => {
    if (!content.trim()) {
      alert('意見を入力してください。');
      return;
    }
    setShowConfirmModal(false);
    setIsLoading(true);

    try {
      const token = await getToken();
      const position = side === 'agree' ? 'AGREE' : 'DISAGREE';

      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${debateId}/messages/post`,
        {
          content: content,
          position: position,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // 成功したらチャット画面へ
      router.push(`/debates/${debateId}`);

    } catch (error) {
      console.error('初回投稿に失敗しました:', error);
      alert('投稿に失敗しました。もう一度お試しください。');
      setIsLoading(false);
    }
  };

  const oppositeSide = side === 'agree' ? '反対' : '賛成';
  const oppositeSideClass = side === 'agree' ? styles.disagree : styles.agree;

  return (
    <div className={styles.pageContainer}>
      <DebateHeader debateId={debateId} side={side} />

      <div className={styles.contentWrapper}>
        <div className={styles.guideBox}>
          <p>あなたは「{side === 'agree' ? '賛成' : '反対'}」を選択しましたが</p>
          <p>
            <span className={oppositeSideClass}>{oppositeSide}の立場</span>で議論してください
          </p>
          <p className={styles.guideSubText}>
            まずは{oppositeSide}の立場に立って<br />
            自分の意見を投稿して議論に参加しましょう
          </p>
        </div>
      </div>

      <CommentInput
        value={content}
        onChange={setContent}
        onSendMessage={handleShowConfirmModal}
        isLoading={isLoading}
        placeholder={`${oppositeSide}意見をここに入力...`}
      />

      {/* 投稿確認モーダル */}
      {showConfirmModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <h2>投稿確認</h2>
            <p className={styles.confirmText}>この内容で最初の意見を投稿しますか？</p>
            {/* ★★★ CSSが効くように、クラス名を修正 ★★★ */}
            <div className={styles.modalButtons}>
              <button onClick={() => setShowConfirmModal(false)} className={styles.modalCancel}>
                戻る
              </button>
              <button onClick={handleSubmit} className={styles.modalConfirm}>
                投稿する
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}