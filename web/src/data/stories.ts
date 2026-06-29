export interface DialogueLine {
  npcText: string;
  npcMood: 'neutral' | 'happy' | 'curious' | 'surprised';
  requiredSignId: string;
  hint: string;
  npcResponse: string;
}

export interface StoryScript {
  id: string;
  title: string;
  description: string;
  npcName: string;
  npcEmoji: string;
  backgroundEmoji: string;
  lines: DialogueLine[];
}

export const COFFEE_SHOP_STORY: StoryScript = {
  id: 'coffee-story',
  title: 'At the Coffee Shop',
  description: 'Order a coffee from Zippy the barista',
  npcName: 'Zippy',
  npcEmoji: '🤟',
  backgroundEmoji: '☕',
  lines: [
    {
      npcText: "Hey there! Welcome to Zippy's Coffee! Can you say hello?",
      npcMood: 'happy',
      requiredSignId: 'HELLO',
      hint: 'Wave hello!',
      npcResponse: "Hi! Great to see you! 👋",
    },
    {
      npcText: "What can I get for you today?",
      npcMood: 'curious',
      requiredSignId: 'COFFEE',
      hint: 'Two fists, grind the top over the bottom',
      npcResponse: "A coffee, coming right up! ☕",
    },
    {
      npcText: "Anything else you'd like?",
      npcMood: 'neutral',
      requiredSignId: 'PLEASE',
      hint: 'Circle your open hand on your chest',
      npcResponse: "Of course! Since you asked so nicely 😊",
    },
    {
      npcText: "Do you want milk with that?",
      npcMood: 'curious',
      requiredSignId: 'YES',
      hint: 'Nod your fist up and down',
      npcResponse: "Milk it is! 🥛",
    },
    {
      npcText: "Here's your coffee! That'll be $4.50.",
      npcMood: 'happy',
      requiredSignId: 'THANK_YOU',
      hint: 'Flat hand from chin, move outward',
      npcResponse: "You're welcome! Have a great day! 💜",
    },
  ],
};

export const STORIES: StoryScript[] = [COFFEE_SHOP_STORY];
