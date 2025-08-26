'use client';

import DebateContent, { Debate } from './Content';
import styles from '../../css/Debates.module.css';
import React, { forwardRef } from 'react'; // forwardRefをインポート

interface Props {
  debates: Debate[];
  onDebateClick: (debateId: number) => void;
}


export default function ContentList({ debates, onDebateClick} :Props)  {
  return (
    <section className={styles.listSection}>
      {/* titleはタブで表示するので不要に */}
      {debates.length > 0 ? (
        <div className={styles.listGrid}>
          {debates.map((debate, index) => {
            // 最後の要素にrefをアタッチ
            if (debates.length === index + 1) {
              return (
                <div key={debate.id}>
                  <DebateContent debate={debate} onClick={() => onDebateClick(debate.id)} />
                </div>
              );
            }
            return <DebateContent key={debate.id} debate={debate} onClick={() => onDebateClick(debate.id)} />;
          })}
        </div>
      ) : (
        <p>該当するディベートはありません。</p>
      )}
    </section>
  );
}
