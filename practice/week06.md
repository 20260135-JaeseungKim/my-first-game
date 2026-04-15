# Week 6 실습 기록

## 사용한 에셋
- 이미지: (파일명, 출처)
- 사운드: (파일명, 출처)

## 사용한 AI 프롬프트

**Q1: 파이게임에서 이미지 적용하는 방법 알려줘

-AI 답변: image = pygame.image.load("이미지파일경로.png") 이런 식으로 이미지를 불러오고 
player_img = pygame.transform.scale(player_img, (100, 100)) 크기를 조절한 다음 
screen.blit(player_img, (x, y)) 화면에 그리면 됨
pygame.display.update() 이후 업데이트 하기


**Q2: 사운드 적용하는 방법

-AI 답변: pygame.mixer.init() 게임 시작할 때 한 번 실행하면서 기본 설정을 해
효과음은 shoot_sound = pygame.mixer.Sound("shoot.wav") 이 코드로 불러오고
shoot_sound.play() 이 코드로 재생
shoot_sound.set_volume(0.5) 이건 볼륨 조절

pygame.mixer.music.load("bgm.mp3") 이건 배경음악 불러오기
pygame.mixer.music.play(-1)  # -1 = 무한 반복 
pygame.mixer.music.stop() 정지는 이렇게


## AI 답변에서 도움이 된 것
기본적으로 파이게임에서 효과음, 배경음악, 이미지 등을 불러오고 사용하는 방법에 대해 효과적으로 이해하게 되었으며, 전체적인 흐름도 파악할 수 있게 되었다.

## AI 답변을 수정하거나 버린 것
없음

## 적용 결과
- 잘 된 것: 테스트로 이미지랑 사운드 삽입해보기
- 어려웠던 것: 에셋 찾기(이미지, 사운드 등)
- 다음에 시도할 것: 이미지와 사운드를 찾고 적용하고 애니메이션 까지 적용해보기
