'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import axios from 'axios';
import ContentList from '@/app/components/content/ContentList';
import { Debate } from '@/app/types/debate';
import styles from '@/app/css/Profile.module.css'; // この画面専用のCSS
import { DebateDetailData } from '@/app/types/debate';
import ContentDetail from '@/app/components/content/ContentDetail';

// プロフィール情報の型
interface ProfileData {
  user_name: string;
  participated_count: number;
}

export default function ProfilePage() {
  const params = useParams<{ userName: string }>();
  const { getToken } = useAuth();

  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [createdDebates, setCreatedDebates] = useState<Debate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // モーダル関連のState
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedDebateId, setSelectedDebateId] = useState<number | null>(null);
  const [debateDetail, setDebateDetail] = useState<DebateDetailData | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const token = await getToken();
        // プロフィール情報と、作成したディベート一覧を、同時に取得！
        const [profileRes, createdDebatesRes] = await Promise.all([
          axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/profile/`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/user/me/created_debates/`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);
        setProfile(profileRes.data);
        setCreatedDebates(createdDebatesRes.data);
      } catch (error) {
        console.error("プロフィール情報の取得に失敗", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfileData();
  }, [getToken]);

  // 4. 個別ディベートの詳細を取得
  useEffect(() => {
    if (selectedDebateId !== null) {
      const fetchDebateDetail = async () => {
        setIsDetailLoading(true);
        try {
          const token = await getToken();
          const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/${selectedDebateId}/`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setDebateDetail(response.data);
        } catch (error) {
          console.error("ディベート詳細の取得に失敗しました:", error);
          setDebateDetail(null);
        } finally {
          setIsDetailLoading(false);
        }
      };
      fetchDebateDetail();
    }
  }, [selectedDebateId, getToken]);

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedDebateId(null);
    setDebateDetail(null);
  };

  const handleDebateClick = (debateId: number) => {
    setSelectedDebateId(debateId);
    setIsModalOpen(true);
  };

  if (isLoading) return <div>読み込み中...</div>;
  if (!profile) return <div>プロフィールを取得できませんでした。</div>;

  return (
    <div className={styles.container}>
      <div className={styles.profileHeader}>
        <h1 className={styles.userName}>{profile.user_name}</h1>
        <div className={styles.stats}>
          参加ディベート数: {profile.participated_count}
        </div>
      </div>

      <div className={styles.debatesSection}>
        <h2 className={styles.title}>作成したディベート（{createdDebates.length}）</h2>
        <ContentList
          debates={createdDebates}
          onDebateClick={handleDebateClick}
        />
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <ContentDetail debateDetail={debateDetail} isLoading={isDetailLoading} />
          </div>
        </div>
      )}
    </div>
  );
}