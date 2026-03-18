import { HeroSection } from '@/components/landing/HeroSection';
import { FeatureCards } from '@/components/landing/FeatureCards';
import { WorkflowSection } from '@/components/landing/WorkflowSection';
import { CTASection } from '@/components/landing/CTASection';

export default function Home() {
  return (
    <div>
      <HeroSection />
      <FeatureCards />
      <WorkflowSection />
      <CTASection />
    </div>
  );
}
