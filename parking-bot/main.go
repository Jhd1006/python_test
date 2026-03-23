package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
)

// 서버 규격에 맞춘 구조체
type ParkingEvent struct {
	VehicleNum  string    `json:"vehicle_num"`
	VehicleType string    `json:"vehicle_type"` // General, EV, Disabled
	ZoneID      int       `json:"zone_id"`      // 1
	SlotCode    string    `json:"slot_code"`    // A001 형식
	Status      string    `json:"status"`       // PARKED 또는 EXITED
	UpdateAt    time.Time `json:"update_at"`
}

type ParkedCar struct {
	VehicleNum  string
	VehicleType string
}

var (
	parkingLot  = make(map[string]ParkedCar)
	lotMutex    sync.Mutex
	maxSlots    = 100
	fixedZoneID = 1
)

func generatePlate() string {
	chars := []string{"가", "나", "다", "라", "마", "바", "사", "아", "자", "차"}
	front := rand.Intn(900) + 100
	char := chars[rand.Intn(len(chars))]
	back := rand.Intn(9000) + 1000
	return fmt.Sprintf("%03d%s%04d", front, char, back)
}

func generateVehicleType() string {
	types := []string{"General", "EV", "Disabled"}
	return types[rand.Intn(len(types))]
}

func sendParkingEvent(baseApiUrl string, event ParkingEvent) {
	var targetUrl string
	action := ""

	// 1. baseApiUrl에서 마지막 슬래시 제거 (중복 방지)
	cleanBaseUrl := strings.TrimSuffix(baseApiUrl, "/")

	// 2. 서버 urls.py 규격에 맞춰 슬래시 없이 URL 생성
	if event.Status == "PARKED" {
		targetUrl = fmt.Sprintf("%s/entries", cleanBaseUrl)
		action = "입차(ENTRY)"
	} else {
		targetUrl = fmt.Sprintf("%s/exits", cleanBaseUrl)
		action = "출차(EXIT)"
	}

	jsonData, err := json.Marshal(event)
	if err != nil {
		fmt.Println("❌ JSON 변환 오류:", err)
		return
	}

	req, err := http.NewRequest("POST", targetUrl, bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Println("❌ HTTP 요청 생성 오류:", err)
		return
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Idempotency-Key", uuid.New().String())

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)

	if err != nil {
		fmt.Printf("❌ 전송 실패 | %s | %s | 사유: %v\n", action, event.VehicleNum, err)
		return
	}
	defer resp.Body.Close()

	fmt.Printf("✅ 전송 시도 | %s | %s | URL: %s | 상태: %d\n", 
		action, event.VehicleNum, targetUrl, resp.StatusCode)
}

func main() {
	apiUrl := os.Getenv("API_URL")
	if apiUrl == "" {
		apiUrl = "http://orchestration-http:8000/api/v1/parking"
	}

	rand.Seed(time.Now().UnixNano())
	fmt.Printf("🚀 주차장 트래픽 봇 가동 시작 (Target: %s)\n", apiUrl)

	for {
		now := time.Now()
		hour := now.Hour()
		burstCount := 1
		sleepTime := 2 * time.Second

		// 피크 타임 로직
		if (hour >= 8 && hour <= 9) || (hour >= 18 && hour <= 19) {
			burstCount = 5
			sleepTime = 500 * time.Millisecond
		}

		for i := 0; i < burstCount; i++ {
			lotMutex.Lock()
			isEntry := true
			if len(parkingLot) >= maxSlots {
				isEntry = false
			} else if len(parkingLot) > 0 {
				isEntry = rand.Intn(2) == 0
			}

			var event ParkingEvent
			if isEntry {
				slotNum := rand.Intn(maxSlots) + 1
				slotCode := fmt.Sprintf("A%03d", slotNum)
				
				// 중복 점유 방지
				if _, exists := parkingLot[slotCode]; !exists {
					plate := generatePlate()
					vType := generateVehicleType()
					parkingLot[slotCode] = ParkedCar{VehicleNum: plate, VehicleType: vType}
					
					event = ParkingEvent{
						VehicleNum:  plate,
						VehicleType: vType,
						ZoneID:      fixedZoneID,
						SlotCode:    slotCode,
						Status:      "PARKED",
						UpdateAt:    time.Now(),
					}
					go sendParkingEvent(apiUrl, event)
				}
			} else {
				// 랜덤 출차
				for slot, car := range parkingLot {
					event = ParkingEvent{
						VehicleNum:  car.VehicleNum,
						VehicleType: car.VehicleType,
						ZoneID:      fixedZoneID,
						SlotCode:    slot,
						Status:      "EXITED",
						UpdateAt:    time.Now(),
					}
					delete(parkingLot, slot)
					go sendParkingEvent(apiUrl, event)
					break
				}
			}
			lotMutex.Unlock()
		}
		time.Sleep(sleepTime)
	}
}
