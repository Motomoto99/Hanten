'use client';

import { useState, useRef, useEffect } from 'react';
import styles from '../../css/CommentInput.module.css';

interface Props {
    value: string;
    onChange: (value: string) => void;
    // 親コンポーネントに「送信」イベントを通知するための関数
    onSendMessage: (content: string) => void;
    isLoading?: boolean; // 親が読み込み中かどうか
    placeholder?: string;
}

export default function CommentInput({
    value,
    onChange,
    onSendMessage,
    isLoading = false,
    placeholder = "メッセージを入力..."
}: Props) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if (value.trim() && !isLoading) {
            onSendMessage(value.trim());
            textareaRef.current?.focus();
        }
    };

    // ★★★ テキストエリアの高さを自動調整する魔法 ★★★
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'; // 一旦高さをリセット
            const scrollHeight = textareaRef.current.scrollHeight;
            textareaRef.current.style.height = `${scrollHeight}px`;
        }
    }, [value]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        // Ctrlキー（MacならCmdキー）と、Enterキーが、同時に押されたら…
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault(); // 元々のEnterキーの動作（改行）をキャンセル
            handleSend(); // そして、送信処理を呼び出す！
        }
    };

    return (
        <div className={styles.container}>
            <textarea
                ref={textareaRef}
                className={styles.textarea}
                value={value}
                maxLength={500}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                rows={1} // 最初は1行で表示
                disabled={isLoading}
                onKeyDown={handleKeyDown} 
            />
            <button
                onClick={handleSend}
                // ★★★ テキストが入力されたら表示されるボタン ★★★
                className={`${styles.sendButton} ${value.trim() ? styles.visible : ''}`}
                disabled={!value.trim() || isLoading}
                aria-label="送信"
            >
                {/* 送信アイコン（SVG） */}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393" />
                </svg>
            </button>
        </div>
    );
}