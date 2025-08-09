'use client';

import DebateContent, { Debate } from './Content';
import styles from '../../css/Debates.module.css';

interface Props {
    title: string;
    debates: Debate[];
    onDebateClick: (debateId: number) => void;
}

export default function DebateContentList({ title, debates, onDebateClick }: Props) {
    return (
        <section className={styles.listSection}>
            <h2 className={styles.listTitle}>{title}</h2>
            {debates.length > 0 ? (
                <div className={styles.listGrid}>
                    {debates.map((debate) => (
                        <DebateContent
                            key={debate.id}
                            debate={debate}
                            onClick={() => onDebateClick(debate.id)}
                        />
                    ))}
                </div>
            ) : (
                <div>
                    <p>該当するディベートはありません。</p>
                </div>
            )}
        </section>
    );
}