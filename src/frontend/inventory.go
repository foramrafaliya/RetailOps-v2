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

type InventoryData struct {
	ID       string  `json:"id"`
	Name     string  `json:"name"`
	Quantity int     `json:"quantity"`
	Price    float64 `json:"price"`
}

func getInventoryServiceAddr() string {
	addr := os.Getenv("INVENTORY_SERVICE_ADDR")
	if addr == "" {
		addr = "inventoryservice:8084"
	}
	return addr
}

func fetchInventory(productID string) *InventoryData {
	url := fmt.Sprintf("http://%s/inventory/%s", getInventoryServiceAddr(), productID)

	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		fmt.Printf("Failed to fetch inventory: %v\n", err)
		return &InventoryData{ID: productID, Quantity: -1}
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return &InventoryData{ID: productID, Quantity: -1}
	}

	var data InventoryData
	if err := json.Unmarshal(body, &data); err != nil {
		return &InventoryData{ID: productID, Quantity: -1}
	}

	return &data
}
func reduceInventory(productID string, amount int) error {
	url := fmt.Sprintf("http://%s/inventory/%s/reduce", getInventoryServiceAddr(), productID)

	reduceData := map[string]interface{}{
		"amount": amount,
	}

	jsonData, err := json.Marshal(reduceData)
	if err != nil {
		return err
	}

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to call inventory service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("inventory service error: %s", string(body))
	}

	return nil
}