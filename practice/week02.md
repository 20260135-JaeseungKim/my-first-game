# Week 2 실습 기록


## 목표 Git 사용법 학습, git commit 하기, GitHub에 연결하기


## AI 대화 기록
**Q1: 다른 컴퓨터에서 작업하다가 다른 컴퓨터에서 깃허브 내용을 불러오는 방법이 뭐야?
**A1: Git 저장소를 가져오기 위해서는 clone을 사용합니다.
**예: git clone https://github.com/아이디/저장소.git

**Q2: git remote가 무슨 역할이야?
**A2: git remote는 내 컴퓨터의 Git 저장소와 인터넷에 있는 저장소(예: GitHub)를 연결해주는 설정입니다.
**예: git remote add origin https://github.com/아이디/저장소.git

**Q3: git 사용 흐름
**A3: *처음 시작
    git init
    git remote add origin 저장소주소
        \/
    *작업 중(반복)
    git add -> git commit -m "작업 내용" -> git push
        \/
    *최신 코드 불러오기
    git pull

## 어려웠던 점
git의 작동원리와 다양한 git 용어를 이해하는 게 가장 어려웠다. 


## 배운 점
git을 어떻게 사용하고 어떤 흐름으로 작동이 되는지에 대해 알게되었고 직접 데이터를 커밋하고 푸쉬하며 사용방법에 대해 잘 알게되었다.
