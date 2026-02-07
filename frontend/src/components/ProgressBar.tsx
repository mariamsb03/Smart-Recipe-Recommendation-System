import { Check } from 'lucide-react';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  labels?: string[];
}

export function ProgressBar({ currentStep, totalSteps, labels }: ProgressBarProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {Array.from({ length: totalSteps }, (_, i) => {
          const step = i + 1;
          const isCompleted = step < currentStep;
          const isActive = step === currentStep;
          
          return (
            <div key={step} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div
                  className={`progress-step ${
                    isCompleted
                      ? 'progress-step-completed'
                      : isActive
                      ? 'progress-step-active'
                      : 'progress-step-inactive'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    step
                  )}
                </div>
                {labels && labels[i] && (
                  <span className={`text-xs mt-2 ${
                    isActive ? 'text-primary font-medium' : 'text-muted-foreground'
                  }`}>
                    {labels[i]}
                  </span>
                )}
              </div>
              
              {i < totalSteps - 1 && (
                <div className="flex-1 h-0.5 mx-3 mt-[-20px]">
                  <div
                    className={`h-full transition-colors duration-300 ${
                      isCompleted ? 'bg-accent' : 'bg-border'
                    }`}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
