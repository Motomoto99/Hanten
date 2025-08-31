'use client';

import React from 'react'
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';
import styles from '../../css/Create.module.css';

// テーマの型定義
interface Theme {
  id: number;
  theme_title: string;
  theme_detail: string;
}

export default function page() {
  const [roomName, setRoomName] = useState('');
  const [duration, setDuration] = useState<number | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [allThemes, setAllThemes] = useState<Theme[]>([]);

  const [isThemeModalOpen, setIsThemeModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { getToken } = useAuth();
  const router = useRouter();

  // APIからテーマ一覧を取得
  useEffect(() => {
    const fetchThemes = async () => {
      try {
        const token = await getToken();
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/debate/themes/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAllThemes(response.data);
      } catch (error) {
        console.error("テーマ一覧の取得に失敗しました", error);
      }
    };
    fetchThemes();
  }, [getToken]);

  const handleSubmit = async () => {
    if (!roomName || !duration || !selectedTheme) {
      alert('すべての項目を入力してください。');
      return;
    }
    setIsLoading(true);
    try {
      const token = await getToken();
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/debate/debates/`,
        {
          room_name: roomName,
          duration_hours: duration,
          theme_id: selectedTheme.id,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // 成功したら、作成された部屋のIDをクエリパラメータに付けて一覧ページにリダイレクト
      router.push(`/debates?open=${response.data.id}`);

    } catch (error) {
      console.error("ディベート部屋の作成に失敗しました:", error);
      alert('作成に失敗しました。');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>新しいディベート部屋を作成</h1>

      {/* テーマ選択 */}
      <div className={styles.formGroup}>
        <label>テーマ</label>
        <div className={styles.themeSelector} onClick={() => setIsThemeModalOpen(true)}>
          {selectedTheme ? selectedTheme.theme_title : '議論テーマを選択する'}
        </div>
        {selectedTheme && (
          <p className={styles.themeDetail}>{selectedTheme.theme_detail}</p>
        )}
      </div>

      {/* 部屋名入力 */}
      <div className={styles.formGroup}>
        <label>ディベート部屋名</label>
        <input
          type="text"
          maxLength={50}
          value={roomName}
          onChange={(e) => setRoomName(e.target.value)}
          placeholder="例：消費税について話したい　（50字以内）"
        />
      </div>

      {/* 開催期間選択 */}
      <div className={styles.formGroup}>
        <label>開催期間</label>
        <div className={styles.durationButtons}>
          {[24, 48, 72].map((hours) => (
            <button
              key={hours}
              className={duration === hours ? styles.active : ''}
              onClick={() => setDuration(hours)}
            >
              {hours}時間
            </button>
          ))}
        </div>
      </div>

      {/* 作成ボタン */}
      <div className={styles.actionButtons}>
        <button onClick={() => router.back()} className={styles.backButton}>戻る</button>
        <button onClick={handleSubmit} disabled={isLoading} className={styles.createButton}>
          {isLoading ? '作成中...' : '作成'}
        </button>
      </div>

      {/* テーマ選択モーダル */}
      {isThemeModalOpen && (
        <div className={styles.modalOverlay} onClick={() => setIsThemeModalOpen(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>テーマを選択</h2>
              <button onClick={() => setIsThemeModalOpen(false)} className={styles.closeButton}>×</button>
            </div>
            <div className={styles.themeList}>
              {allThemes.map((theme) => (
                <div
                  key={theme.id}
                  className={`${styles.themeItem} ${selectedTheme?.id === theme.id ? styles.selected : ''}`}
                  onClick={() => {
                    setSelectedTheme(theme);
                    setIsThemeModalOpen(false);
                  }}
                >
                  <h3>{theme.theme_title}</h3>
                  <p>{theme.theme_detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
