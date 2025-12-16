import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  emoji: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Comprehensive Coverage',
    emoji: '🤖',
    description: (
      <>
        Master the fundamentals of Physical AI and humanoid robotics, from locomotion
        and manipulation to sensing and control. Build a solid foundation in both
        theory and practice.
      </>
    ),
  },
  {
    title: 'Interactive Learning',
    emoji: '🧠',
    description: (
      <>
        Engage with AI-powered learning assistants that explain concepts, quiz your
        understanding, and guide you through hands-on lab exercises. Learn by doing
        with interactive examples.
      </>
    ),
  },
  {
    title: 'Real-World Applications',
    emoji: '⚙️',
    description: (
      <>
        Explore practical examples from Boston Dynamics, surgical robotics, and
        collaborative systems. Access simulation-ready code samples and solve
        real-world robotics challenges.
      </>
    ),
  },
];

function Feature({title, emoji, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <div className={styles.featureEmoji}>{emoji}</div>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
