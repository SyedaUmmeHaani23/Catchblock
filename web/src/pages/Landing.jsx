import { Hero } from '../components/Hero'
import { FindingsReel } from '../components/FindingsReel'
import { HeartbeatStory } from '../components/HeartbeatStory'
import { Features } from '../components/Features'
import { FinalCta } from '../components/FinalCta'

export default function Landing({ onScan }) {
  return (
    <main>
      <Hero onScan={onScan} />
      <FindingsReel />
      <HeartbeatStory />
      <Features />
      <FinalCta onScan={onScan} />
    </main>
  )
}
