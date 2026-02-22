package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type Review struct {
	ID        string `json:"id"`
	User      string `json:"user"`
	Rating    int    `json:"rating"`
	Comment   string `json:"comment"`
	CreatedAt string `json:"created_at"`
}

type ReviewData struct {
	ProductID    string   `json:"product_id"`
	TotalReviews int      `json:"total_reviews"`
	AvgRating    float64  `json:"average_rating"`
	Reviews      []Review `json:"reviews"`
}

func getReviewServiceAddr() string {
	addr := os.Getenv("REVIEW_SERVICE_ADDR")
	if addr == "" {
		addr = "reviewservice:8085"
	}
	return addr
}

func fetchReviews(productID string) *ReviewData {
	url := fmt.Sprintf("http://%s/reviews/%s", getReviewServiceAddr(), productID)

	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		fmt.Printf("Failed to fetch reviews: %v\n", err)
		return &ReviewData{ProductID: productID, Reviews: []Review{}}
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return &ReviewData{ProductID: productID, Reviews: []Review{}}
	}

	var data ReviewData
	if err := json.Unmarshal(body, &data); err != nil {
		return &ReviewData{ProductID: productID, Reviews: []Review{}}
	}

	return &data
}

func submitReviewToService(productID, user string, rating int, comment string) error {
	url := fmt.Sprintf("http://%s/reviews", getReviewServiceAddr())

	reviewData := map[string]interface{}{
		"product_id": productID,
		"user":       user,
		"rating":     rating,
		"comment":    comment,
	}

	jsonData, err := json.Marshal(reviewData)
	if err != nil {
		return err
	}

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 201 {
		return fmt.Errorf("review service returned status: %d", resp.StatusCode)
	}

	return nil
}