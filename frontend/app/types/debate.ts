// このファイルは、ディベート機能で共通して使う「型」だけを定義する、部品カタログです。

// メッセージの型定義
export interface Message {
    id: number;
    sender: {
        user_name: string;
        clerk_user_id: string;
    };
    content: string;
    created_at: string;
}

// 詳細APIから受け取る型
export interface DebateDetailData {
    id: number;
    room_name: string;
    room_start: string;
    room_end: string;
    theme: {
        id: number;
        theme_title: string;
        theme_detail: string;
    };
    // 他にもcreator情報など
    is_participating: boolean; // ユーザーが参加中かどうか
    user_participation: { position: string | null; };
}