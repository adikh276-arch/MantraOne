import { create } from 'zustand';

interface OnboardingState {
  step: 'welcome' | 'create_family' | 'add_members' | 'upload_reports' | 'first_conversation';
  familyData: {
    name?: string;
    members?: Array<{ id: string; name: string; age: number; relationship: string }>;
  };
  setStep: (step: OnboardingState['step']) => void;
  updateFamilyData: (data: Partial<OnboardingState['familyData']>) => void;
}

export const useOnboardingStore = create<OnboardingState>((set) => ({
  step: 'welcome',
  familyData: {},
  setStep: (step) => set({ step }),
  updateFamilyData: (data) => set((state) => ({ familyData: { ...state.familyData, ...data } })),
}));
