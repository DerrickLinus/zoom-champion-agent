export const quizAnimalNames = ['狐獴', '白脸僧面猴', '考拉', '水獭', '小熊猫'] as const

export const companionQuiz = [
  {
    question: '讲解节奏？',
    options: [
      { label: '快一点', scores: [3, 0, 2, 1, 0] },
      { label: '刚刚好', scores: [1, 2, 1, 2, 3] },
      { label: '慢一点', scores: [0, 3, 0, 2, 1] },
    ],
  },
  {
    question: '讲解长度？',
    options: [
      { label: '简短', scores: [2, 0, 3, 0, 1] },
      { label: '适中', scores: [2, 1, 1, 1, 3] },
      { label: '详细', scores: [0, 3, 0, 3, 1] },
    ],
  },
  {
    question: '喜欢什么语气？',
    options: [
      { label: '热情有戏', scores: [1, 0, 0, 3, 1] },
      { label: '轻快自然', scores: [3, 1, 1, 2, 2] },
      { label: '平静克制', scores: [0, 3, 3, 0, 2] },
    ],
  },
  {
    question: '希望它像谁？',
    options: [
      { label: '专业老师', scores: [0, 4, 2, 0, 1] },
      { label: '温柔长辈', scores: [1, 0, 2, 0, 4] },
      { label: '故事朋友', scores: [3, 0, 0, 4, 1] },
    ],
  },
] as const

export function recommendCompanion(answerIndexes: number[]) {
  const totals = quizAnimalNames.map(() => 0)
  const perQuestion = companionQuiz.map((question, questionIndex) => {
    const optionIndex = answerIndexes[questionIndex]
    const option = question.options[optionIndex]
    const scores = option ? [...option.scores] : quizAnimalNames.map(() => 0)
    scores.forEach((score, animalIndex) => { totals[animalIndex] += score })
    return scores
  })

  const matchScores = quizAnimalNames.map((_, animalIndex) =>
    totals[animalIndex]
    + perQuestion[3][animalIndex] * 0.1
    + perQuestion[2][animalIndex] * 0.01
    + perQuestion[1][animalIndex] * 0.001
    + perQuestion[0][animalIndex] * 0.0001
  )

  const ranked = quizAnimalNames.map((_, index) => index).sort((left, right) =>
    matchScores[right] - matchScores[left] || left - right
  )

  return { index: ranked[0], totals, matchScores, ranked }
}
