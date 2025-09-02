import FirstAddComponent from '@/app/components/chat/FirstAddComponent';

// サーバーコンポーネントは、クライアントコンポーネントを呼び出すだけのシンプルなものに
export default function FirstAddPage() {
    return (
        // ★★★ paramsを渡すのをやめます！ ★★★
        <FirstAddComponent />
    );
}